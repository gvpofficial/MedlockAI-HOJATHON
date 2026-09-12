from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from app.agents.agent_verification import run_prescription_verification_agent
from app.agents.agent_integrity import run_dispensing_integrity_agent
from app.agents.agent_pattern import run_cross_pharmacy_pattern_agent
from app.agents.agent_risk_engine import run_risk_assessment_engine
from app.agents.agent_summary_llm import run_review_summary_agent
from app.models.prescription import Prescription, PrescriptionItem
from app.schemas.agent import (
    MultiAgentEvaluationResult,
    DecisionTimelineStep,
    VerificationAgentResult,
    IntegrityAgentResult,
    PatternAgentResult,
    RiskAgentResult,
    SummaryAgentResult
)


def run_medlock_agent_orchestrator(
    db: Session,
    prescription_code: str,
    requested_quantity: int,
    pharmacy_id: str,
    medicine_name: Optional[str] = None,
    prescription_item_id: Optional[str] = None
) -> Tuple[MultiAgentEvaluationResult, Optional[Prescription], Optional[PrescriptionItem]]:
    timeline: List[DecisionTimelineStep] = []

    # STEP 1: Prescription Verification Agent
    verification_res, prescription, target_item = run_prescription_verification_agent(
        db=db,
        prescription_code=prescription_code,
        medicine_name=medicine_name,
        prescription_item_id=prescription_item_id
    )

    if not verification_res.valid:
        timeline.append(
            DecisionTimelineStep(
                step_number=1,
                agent_name="Prescription Verification Agent",
                status="DANGER",
                title="Prescription Verification Failed",
                description=verification_res.rejection_reason or "Prescription invalid or unverified.",
                data={"prescription_status": verification_res.prescription_status}
            )
        )
        
        # Fast exit for invalid prescription
        dummy_integrity = IntegrityAgentResult(
            medicine_name=medicine_name or "Unknown",
            authorized_quantity=0,
            dispensed_quantity=0,
            remaining_quantity=0,
            requested_quantity=requested_quantity,
            allowed=False,
            max_permissible_quantity=0,
            is_partial_possible=False,
            reason="Prescription validation failed."
        )
        dummy_pattern = PatternAgentResult(
            distinct_pharmacies_24h=1,
            distinct_pharmacies_2h=1,
            online_pharmacy_accessed=False,
            recent_rejected_attempts_48h=0,
            rapid_provider_switching_detected=False,
            burst_after_rejection_detected=False,
            anomaly_detected=False,
            pattern_reasons=[]
        )
        dummy_risk = RiskAgentResult(
            risk_score=100,
            risk_level="CRITICAL",
            risk_factors=[],
            recommended_action="RESTRICT_CRITICAL_REVIEW"
        )
        dummy_summary = SummaryAgentResult(
            clinical_summary=f"Prescription rejected during primary verification: {verification_res.rejection_reason}",
            key_evidence=[verification_res.rejection_reason or "Invalid prescription"],
            requires_human_review=False
        )
        
        return MultiAgentEvaluationResult(
            decision="REJECTED",
            prescription_code=prescription_code,
            medicine_name=medicine_name or "Unknown",
            requested_quantity=requested_quantity,
            approved_quantity=0,
            remaining_before=0,
            remaining_after=0,
            risk_score=100,
            risk_level="CRITICAL",
            verification=verification_res,
            integrity=dummy_integrity,
            pattern=dummy_pattern,
            risk=dummy_risk,
            summary=dummy_summary,
            timeline=timeline,
            requires_pharmacist_review=False
        ), prescription, target_item

    timeline.append(
        DecisionTimelineStep(
            step_number=1,
            agent_name="Prescription Verification Agent",
            status="SUCCESS",
            title="Prescription & Doctor Verified",
            description=f"Prescription {prescription.prescription_code} is ACTIVE. Physician and patient identity confirmed.",
            data={
                "prescription_status": prescription.status,
                "expiry": prescription.expiry_date.isoformat()
            }
        )
    )

    # STEP 2: Dispensing Integrity Agent
    integrity_res = run_dispensing_integrity_agent(
        db=db,
        item=target_item,
        requested_quantity=requested_quantity
    )

    if integrity_res.allowed:
        timeline.append(
            DecisionTimelineStep(
                step_number=2,
                agent_name="Dispensing Integrity Agent",
                status="SUCCESS",
                title="Dispensing Limits Verified",
                description=f"Authorized: {integrity_res.authorized_quantity} | Dispensed: {integrity_res.dispensed_quantity} | Remaining: {integrity_res.remaining_quantity}. Requested: {requested_quantity}.",
                data={
                    "authorized": integrity_res.authorized_quantity,
                    "dispensed": integrity_res.dispensed_quantity,
                    "remaining": integrity_res.remaining_quantity
                }
            )
        )
    else:
        timeline.append(
            DecisionTimelineStep(
                step_number=2,
                agent_name="Dispensing Integrity Agent",
                status="DANGER",
                title="Excess Quantity Limit Detected",
                description=integrity_res.reason or "Requested quantity exceeds remaining authorized balance.",
                data={
                    "authorized": integrity_res.authorized_quantity,
                    "dispensed": integrity_res.dispensed_quantity,
                    "remaining": integrity_res.remaining_quantity,
                    "requested": requested_quantity
                }
            )
        )

    # STEP 3: Cross-Pharmacy Pattern Agent
    pattern_res = run_cross_pharmacy_pattern_agent(
        db=db,
        prescription_id=prescription.id,
        current_pharmacy_id=pharmacy_id
    )

    if pattern_res.anomaly_detected:
        timeline.append(
            DecisionTimelineStep(
                step_number=3,
                agent_name="Cross-Pharmacy Pattern Agent",
                status="WARNING",
                title="Cross-Pharmacy Anomaly Identified",
                description=" | ".join(pattern_res.pattern_reasons),
                data={
                    "distinct_pharmacies_2h": pattern_res.distinct_pharmacies_2h,
                    "distinct_pharmacies_24h": pattern_res.distinct_pharmacies_24h,
                    "rapid_switching": pattern_res.rapid_provider_switching_detected
                }
            )
        )
    else:
        timeline.append(
            DecisionTimelineStep(
                step_number=3,
                agent_name="Cross-Pharmacy Pattern Agent",
                status="SUCCESS",
                title="Cross-Pharmacy History Normal",
                description="No rapid provider switching or burst purchase anomalies detected across the participating network.",
                data={"distinct_pharmacies_24h": pattern_res.distinct_pharmacies_24h}
            )
        )

    # STEP 4: Risk Assessment Engine
    risk_res = run_risk_assessment_engine(
        integrity_result=integrity_res,
        pattern_result=pattern_res
    )

    risk_step_status = "SUCCESS" if risk_res.risk_level == "LOW" else ("WARNING" if risk_res.risk_level == "MEDIUM" else "DANGER")
    timeline.append(
        DecisionTimelineStep(
            step_number=4,
            agent_name="Risk Assessment Engine",
            status=risk_step_status,
            title=f"Risk Score Computed: {risk_res.risk_score}/100 ({risk_res.risk_level})",
            description=f"Action Category: {risk_res.recommended_action}. Evaluated {len(risk_res.risk_factors)} risk factors.",
            data={
                "risk_score": risk_res.risk_score,
                "risk_level": risk_res.risk_level,
                "factors": [f.factor_name for f in risk_res.risk_factors]
            }
        )
    )

    # STEP 5: Review Summary Agent (LLM / Structured Clinical Synthesis)
    summary_res = run_review_summary_agent(
        verification=verification_res,
        integrity=integrity_res,
        pattern=pattern_res,
        risk=risk_res
    )

    timeline.append(
        DecisionTimelineStep(
            step_number=5,
            agent_name="Review Summary Agent",
            status="INFO",
            title="Clinical Summary Synthesized",
            description=summary_res.clinical_summary,
            data={"requires_human_review": summary_res.requires_human_review}
        )
    )

    # FINAL DECISION GATE
    # Hard Deterministic Gate First:
    final_decision = "APPROVED"
    approved_qty = 0
    remaining_before = integrity_res.remaining_quantity
    remaining_after = remaining_before

    if not integrity_res.allowed:
        final_decision = "REJECTED"
        approved_qty = 0
        remaining_after = remaining_before
        timeline.append(
            DecisionTimelineStep(
                step_number=6,
                agent_name="Central Decision Gate",
                status="DANGER",
                title="Transaction Rejected: Over-Limit",
                description=f"Dispensing rejected. Requested {requested_quantity} units exceeds available balance of {remaining_before} units.",
                data={"decision": "REJECTED"}
            )
        )
    elif risk_res.risk_level in ["HIGH", "CRITICAL"]:
        final_decision = "ON_HOLD"
        approved_qty = 0
        remaining_after = remaining_before
        timeline.append(
            DecisionTimelineStep(
                step_number=6,
                agent_name="Central Decision Gate",
                status="DANGER",
                title="Transaction Placed On Hold for Pharmacist Review",
                description=f"High risk score ({risk_res.risk_score}/100) triggered automated safety hold. Escalated to triage review.",
                data={"decision": "ON_HOLD", "risk_score": risk_res.risk_score}
            )
        )
    else:
        final_decision = "APPROVED"
        approved_qty = requested_quantity
        remaining_after = max(0, remaining_before - approved_qty)
        timeline.append(
            DecisionTimelineStep(
                step_number=6,
                agent_name="Central Decision Gate",
                status="SUCCESS",
                title="Dispensing Approved",
                description=f"Approved {approved_qty} units of {target_item.medicine_name}. New remaining balance: {remaining_after} units.",
                data={"decision": "APPROVED", "approved_quantity": approved_qty, "remaining_after": remaining_after}
            )
        )

    requires_review = (final_decision == "ON_HOLD") or (risk_res.risk_level in ["HIGH", "CRITICAL"])

    result = MultiAgentEvaluationResult(
        decision=final_decision,
        prescription_code=prescription.prescription_code,
        medicine_name=target_item.medicine_name,
        requested_quantity=requested_quantity,
        approved_quantity=approved_qty,
        remaining_before=remaining_before,
        remaining_after=remaining_after,
        risk_score=risk_res.risk_score,
        risk_level=risk_res.risk_level,
        verification=verification_res,
        integrity=integrity_res,
        pattern=pattern_res,
        risk=risk_res,
        summary=summary_res,
        timeline=timeline,
        requires_pharmacist_review=requires_review
    )

    return result, prescription, target_item
