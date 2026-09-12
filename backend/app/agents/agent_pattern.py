from datetime import datetime, timedelta, timezone
from typing import List
from sqlalchemy.orm import Session
from app.models.dispensing import DispensingTransaction, PurchaseAttempt
from app.models.pharmacy import Pharmacy
from app.schemas.agent import PatternAgentResult


def run_cross_pharmacy_pattern_agent(
    db: Session,
    prescription_id: str,
    current_pharmacy_id: str
) -> PatternAgentResult:
    now = datetime.now(timezone.utc)
    reasons: List[str] = []
    
    time_24h_ago = now - timedelta(hours=24)
    time_2h_ago = now - timedelta(hours=2)
    time_48h_ago = now - timedelta(hours=48)
    time_30m_ago = now - timedelta(minutes=30)
    
    # 1. Fetch all transactions & attempts for this prescription across all pharmacies
    transactions_24h = (
        db.query(DispensingTransaction)
        .filter(DispensingTransaction.prescription_id == prescription_id)
        .all()
    )
    
    attempts_48h = (
        db.query(PurchaseAttempt)
        .filter(PurchaseAttempt.prescription_id == prescription_id)
        .all()
    )
    
    # Filter by time safely
    tx_24h = []
    tx_2h = []
    for tx in transactions_24h:
        ts = tx.transaction_timestamp
        if ts:
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts >= time_24h_ago:
                tx_24h.append(tx)
            if ts >= time_2h_ago:
                tx_2h.append(tx)

    att_48h_filtered = []
    att_burst_filtered = []
    for att in attempts_48h:
        ts = att.attempt_timestamp
        if ts:
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts >= time_48h_ago:
                att_48h_filtered.append(att)
            if ts >= time_30m_ago and att.outcome in ["REJECTED", "BLOCKED"]:
                att_burst_filtered.append(att)

    # Track all unique pharmacies across transactions and attempts
    pharmacy_ids_24h = set(tx.pharmacy_id for tx in tx_24h)
    pharmacy_ids_24h.update(att.pharmacy_id for att in att_48h_filtered)
    pharmacy_ids_24h.add(current_pharmacy_id)
    
    pharmacy_ids_2h = set(tx.pharmacy_id for tx in tx_2h)
    pharmacy_ids_2h.update(att.pharmacy_id for att in att_burst_filtered)
    pharmacy_ids_2h.add(current_pharmacy_id)
    
    distinct_24h = len(pharmacy_ids_24h)
    distinct_2h = len(pharmacy_ids_2h)
    
    rapid_switching = distinct_2h >= 2
    if rapid_switching:
        reasons.append(f"Rapid provider switching: {distinct_2h} distinct pharmacies accessed within a 2-hour window.")
    elif distinct_24h >= 3:
        reasons.append(f"Multi-provider pattern: {distinct_24h} different pharmacies visited in the last 24 hours.")

    # 3. Check Online vs Physical pharmacy mixture
    pharmacies = db.query(Pharmacy).filter(Pharmacy.id.in_(pharmacy_ids_24h)).all()
    types = set(p.pharmacy_type for p in pharmacies)
    has_online = "ONLINE" in types
    has_physical = ("PHYSICAL_CHAIN" in types) or ("INDEPENDENT" in types)
    
    if has_online and has_physical and len(pharmacy_ids_24h) >= 2:
        reasons.append("Hybrid channel pattern: Concurrent access between online and physical brick-and-mortar pharmacies.")

    # 4. Check recent rejected attempts
    recent_rejections = [
        att for att in att_48h_filtered 
        if att.outcome in ["REJECTED", "BLOCKED"]
    ]
    rejection_count = len(recent_rejections)
    if rejection_count >= 1:
        reasons.append(f"Recent rejection history: {rejection_count} rejected purchase attempt(s) recorded in past 48 hours.")
        
    # 5. Check rapid retry after rejection (burst within 30 min)
    burst_after_rejection = len(att_burst_filtered) > 0
    if burst_after_rejection:
        reasons.append("Immediate retry behavior: New purchase attempt submitted within 30 minutes of a rejected transaction.")

    anomaly_detected = len(reasons) > 0

    return PatternAgentResult(
        distinct_pharmacies_24h=distinct_24h,
        distinct_pharmacies_2h=distinct_2h,
        online_pharmacy_accessed=has_online,
        recent_rejected_attempts_48h=rejection_count,
        rapid_provider_switching_detected=rapid_switching,
        burst_after_rejection_detected=burst_after_rejection,
        anomaly_detected=anomaly_detected,
        pattern_reasons=reasons,
        timestamp=now
    )
