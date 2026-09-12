import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy.orm import Session
from app.models.audit import AuditLog


def calculate_entry_hash(
    prev_hash: str,
    timestamp: str,
    event_type: str,
    actor_user_id: Optional[str],
    actor_role: Optional[str],
    target_entity: str,
    target_id: Optional[str],
    details_json: dict
) -> str:
    payload = f"{prev_hash}|{timestamp}|{event_type}|{actor_user_id}|{actor_role}|{target_entity}|{target_id}|{json.dumps(details_json, sort_keys=True)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def log_audit_event(
    db: Session,
    event_type: str,
    target_entity: str,
    target_id: Optional[str] = None,
    actor_user_id: Optional[str] = None,
    actor_role: Optional[str] = None,
    details: Optional[dict] = None
) -> AuditLog:
    if details is None:
        details = {}
        
    # Retrieve last log hash for chain linkage
    last_entry = db.query(AuditLog).order_by(AuditLog.created_at.desc()).first()
    prev_hash = last_entry.sha256_hash if last_entry and last_entry.sha256_hash else "GENESIS_ROOT_HASH_MEDLOCK_2026"
    
    now_iso = datetime.now(timezone.utc).isoformat()
    entry_hash = calculate_entry_hash(
        prev_hash=prev_hash,
        timestamp=now_iso,
        event_type=event_type,
        actor_user_id=actor_user_id,
        actor_role=actor_role,
        target_entity=target_entity,
        target_id=target_id,
        details_json=details
    )
    
    audit_entry = AuditLog(
        event_type=event_type,
        actor_user_id=actor_user_id,
        actor_role=actor_role,
        target_entity=target_entity,
        target_id=target_id,
        details_json=details,
        prev_hash=prev_hash,
        sha256_hash=entry_hash,
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    return audit_entry
