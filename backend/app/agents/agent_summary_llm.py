from datetime import datetime, timezone
from typing import List, Optional
import json
import httpx
from app.core.config import settings
from app.schemas.agent import (
    VerificationAgentResult,
    IntegrityAgentResult,
    PatternAgentResult,
    RiskAgentResult,
    SummaryAgentResult
)


def generate_clinical_summary_deterministic(
    verification: VerificationAgentResult,
    integrity: IntegrityAgentResult,
    pattern: PatternAgentResult,
    risk: RiskAgentResult
) -> SummaryAgentResult:
    now = datetime.now(timezone.utc)
    evidence: List[str] = []
    
    # Compile key evidence
    evidence.append(f"Prescription {verification.prescription_code or 'N/A'}: Status is {verification.prescription_status}.")
    evidence.append(
        f"Item {integrity.medicine_name}: Authorized {integrity.authorized_quantity}, Previously Dispensed {integrity.dispensed_quantity}, Remaining {integrity.remaining_quantity}. Requested: {integrity.requested_quantity}."
    )
    
    if pattern.distinct_pharmacies_2h >= 2:
        evidence.append(f"Patient visited {pattern.distinct_pharmacies_2h} distinct pharmacies in the past 2 hours.")
    elif pattern.distinct_pharmacies_24h > 1:
        evidence.append(f"Patient visited {pattern.distinct_pharmacies_24h} pharmacies in the past 24 hours.")
        
    if pattern.recent_rejected_attempts_48h > 0:
        evidence.append(f"{pattern.recent_rejected_attempts_48h} prior transaction rejections recorded within 48 hours.")

    if pattern.burst_after_rejection_detected:
        evidence.append("Immediate re-attempt detected within 30 minutes of a rejected dispensing request.")

    # Formulate narrative summary
    requires_human = risk.risk_score >= 50 or (not integrity.allowed and integrity.remaining_quantity > 0)
    
    if risk.risk_score == 0 and integrity.allowed:
        summary_text = (
            f"Routine dispensing request for {integrity.requested_quantity} units of {integrity.medicine_name}. "
            f"Prescription is valid and {integrity.remaining_quantity} units remain available in central ledger. "
            f"No anomalous cross-pharmacy patterns detected."
        )
    elif not integrity.allowed and integrity.remaining_quantity == 0:
        summary_text = (
            f"Dispensing attempt blocked. Prescription for {integrity.medicine_name} is already fully exhausted "
            f"({integrity.dispensed_quantity}/{integrity.authorized_quantity} units dispensed). "
            f"No remaining balance available across participating network."
        )
    elif not integrity.allowed and integrity.remaining_quantity > 0:
        summary_text = (
            f"Quantity limit breach: Patient requested {integrity.requested_quantity} units of {integrity.medicine_name}, "
            f"which exceeds the remaining authorized limit of {integrity.remaining_quantity} units "
            f"(Total authorized: {integrity.authorized_quantity}, Previously dispensed: {integrity.dispensed_quantity}). "
            f"Partial dispensing up to {integrity.max_permissible_quantity} units may be permissible upon review."
        )
    elif risk.risk_level in ["HIGH", "CRITICAL"]:
        reasons_str = "; ".join(pattern.pattern_reasons) if pattern.pattern_reasons else "elevated risk parameters"
        summary_text = (
            f"High-risk dispensing alert (Risk Score: {risk.risk_score}/100 - {risk.risk_level}). "
            f"Cross-pharmacy pattern detected: {reasons_str}. "
            f"Although requested quantity ({integrity.requested_quantity}) is within numerical balance ({integrity.remaining_quantity}), "
            f"the rapid multi-provider velocity requires authorized pharmacist or reviewer verification prior to release."
        )
    else:
        summary_text = (
            f"Dispensing request for {integrity.requested_quantity} units of {integrity.medicine_name} evaluated with "
            f"moderate risk score ({risk.risk_score}/100). Remaining balance is {integrity.remaining_quantity} units. "
            f"Standard dispensing authorized with audit trail recorded."
        )

    return SummaryAgentResult(
        clinical_summary=summary_text,
        key_evidence=evidence,
        requires_human_review=requires_human,
        timestamp=now
    )


def run_review_summary_agent(
    verification: VerificationAgentResult,
    integrity: IntegrityAgentResult,
    pattern: PatternAgentResult,
    risk: RiskAgentResult
) -> SummaryAgentResult:
    # If Gemini API key is available, we can optionally enhance the summary while strictly anchoring to evidence
    if settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY) > 10:
        try:
            prompt = (
                f"You are a clinical pharmacy AI assistant for MedLock AI. Generate a 2-3 sentence factual pharmacist review briefing.\n"
                f"RULES:\n"
                f"1. DO NOT make authorization decisions.\n"
                f"2. Reference only the facts provided below.\n"
                f"3. Highlight quantity limits, velocity, and provider count.\n\n"
                f"FACTS:\n"
                f"- Prescription: {verification.prescription_code} (Status: {verification.prescription_status})\n"
                f"- Medicine: {integrity.medicine_name}\n"
                f"- Authorized: {integrity.authorized_quantity}, Dispensed: {integrity.dispensed_quantity}, Remaining: {integrity.remaining_quantity}, Requested: {integrity.requested_quantity}\n"
                f"- Pharmacies in 2h: {pattern.distinct_pharmacies_2h}, in 24h: {pattern.distinct_pharmacies_24h}\n"
                f"- Recent Rejections: {pattern.recent_rejected_attempts_48h}\n"
                f"- Risk Score: {risk.risk_score} ({risk.risk_level})\n"
                f"- Identified Factors: {[f.description for f in risk.risk_factors]}\n"
            )
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 200}
            }
            with httpx.Client(timeout=3.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    deterministic_fallback = generate_clinical_summary_deterministic(verification, integrity, pattern, risk)
                    deterministic_fallback.clinical_summary = text
                    return deterministic_fallback
        except Exception:
            pass  # Fall back seamlessly to deterministic clinical reasoning
            
    return generate_clinical_summary_deterministic(verification, integrity, pattern, risk)
