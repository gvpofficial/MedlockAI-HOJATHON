from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


# Agent 1: Prescription Verification Agent
class VerificationAgentResult(BaseModel):
    agent_name: str = "Prescription Verification Agent"
    valid: bool
    prescription_id: Optional[str] = None
    prescription_code: Optional[str] = None
    prescription_status: str
    expiry_valid: bool
    doctor_verified: bool
    patient_verified: bool
    medicine_match: bool
    rejection_reason: Optional[str] = None
    timestamp: datetime = datetime.now()


# Agent 2: Dispensing Integrity Agent
class IntegrityAgentResult(BaseModel):
    agent_name: str = "Dispensing Integrity Agent"
    item_id: Optional[str] = None
    medicine_name: str
    authorized_quantity: int
    dispensed_quantity: int
    remaining_quantity: int
    requested_quantity: int
    allowed: bool
    max_permissible_quantity: int
    is_partial_possible: bool
    reason: Optional[str] = None
    timestamp: datetime = datetime.now()


# Agent 3: Cross-Pharmacy Pattern Agent
class PatternAgentResult(BaseModel):
    agent_name: str = "Cross-Pharmacy Pattern Agent"
    distinct_pharmacies_24h: int
    distinct_pharmacies_2h: int
    online_pharmacy_accessed: bool
    recent_rejected_attempts_48h: int
    rapid_provider_switching_detected: bool
    burst_after_rejection_detected: bool
    anomaly_detected: bool
    pattern_reasons: List[str] = []
    timestamp: datetime = datetime.now()


# Agent 4: Risk Assessment Engine
class RiskFactor(BaseModel):
    factor_name: str
    score_addition: int
    description: str


class RiskAgentResult(BaseModel):
    agent_name: str = "Risk Assessment Engine"
    risk_score: int  # 0 to 100
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    risk_factors: List[RiskFactor] = []
    recommended_action: str  # APPROVE, PROCEED_WITH_LOG, HOLD_PHARMACIST_REVIEW, RESTRICT_CRITICAL_REVIEW
    timestamp: datetime = datetime.now()


# Agent 5: Review Summary Agent
class SummaryAgentResult(BaseModel):
    agent_name: str = "Review Summary Agent"
    clinical_summary: str
    key_evidence: List[str] = []
    requires_human_review: bool
    timestamp: datetime = datetime.now()


# Timeline Step for UI
class DecisionTimelineStep(BaseModel):
    step_number: int
    agent_name: str
    status: str  # SUCCESS, WARNING, DANGER, INFO
    title: str
    description: str
    data: Dict[str, Any] = {}


# Complete Multi-Agent Evaluation Output
class MultiAgentEvaluationResult(BaseModel):
    decision: str  # APPROVED, PARTIALLY_APPROVED, REJECTED, ON_HOLD, PHARMACIST_REVIEW_REQUIRED
    prescription_code: str
    medicine_name: str
    requested_quantity: int
    approved_quantity: int
    remaining_before: int
    remaining_after: int
    risk_score: int
    risk_level: str
    verification: VerificationAgentResult
    integrity: IntegrityAgentResult
    pattern: PatternAgentResult
    risk: RiskAgentResult
    summary: SummaryAgentResult
    timeline: List[DecisionTimelineStep]
    requires_pharmacist_review: bool
    review_case_id: Optional[str] = None
