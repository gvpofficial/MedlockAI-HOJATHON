from datetime import datetime, timezone
from typing import List
from app.core.config import settings
from app.schemas.agent import (
    IntegrityAgentResult,
    PatternAgentResult,
    RiskAgentResult,
    RiskFactor
)


def run_risk_assessment_engine(
    integrity_result: IntegrityAgentResult,
    pattern_result: PatternAgentResult
) -> RiskAgentResult:
    now = datetime.now(timezone.utc)
    factors: List[RiskFactor] = []
    total_score = 0

    # Factor 1: Quantity Request exceeds remaining balance
    if not integrity_result.allowed:
        score = settings.RISK_WEIGHT_EXCEEDS_QTY
        total_score += score
        factors.append(
            RiskFactor(
                factor_name="QUANTITY_EXCEEDS_REMAINING",
                score_addition=score,
                description=f"Requested quantity ({integrity_result.requested_quantity}) exceeds remaining balance ({integrity_result.remaining_quantity})."
            )
        )

    # Factor 2: Rapid Provider Switching (< 2 hours)
    if pattern_result.rapid_provider_switching_detected:
        score = settings.RISK_WEIGHT_RAPID_SWITCHING
        total_score += score
        factors.append(
            RiskFactor(
                factor_name="RAPID_PROVIDER_SWITCHING",
                score_addition=score,
                description=f"{pattern_result.distinct_pharmacies_2h} distinct pharmacies accessed within 2 hours."
            )
        )
    # Factor 3: Multi-Provider Spike in 24 hours (if not already counted under rapid switching)
    elif pattern_result.distinct_pharmacies_24h >= 3:
        score = settings.RISK_WEIGHT_MULTI_PROVIDER
        total_score += score
        factors.append(
            RiskFactor(
                factor_name="MULTI_PROVIDER_24H",
                score_addition=score,
                description=f"{pattern_result.distinct_pharmacies_24h} different pharmacies accessed in a 24-hour window."
            )
        )

    # Factor 4: Recent Rejections Frequency
    if pattern_result.recent_rejected_attempts_48h >= 1:
        score = settings.RISK_WEIGHT_RECENT_REJECTIONS
        total_score += score
        factors.append(
            RiskFactor(
                factor_name="REPEATED_REJECTIONS",
                score_addition=score,
                description=f"{pattern_result.recent_rejected_attempts_48h} rejected transaction(s) recorded within 48 hours."
            )
        )

    # Factor 5: Immediate Retry After Rejection
    if pattern_result.burst_after_rejection_detected:
        score = settings.RISK_WEIGHT_REATTEMPT_AFTER_DENIAL
        total_score += score
        factors.append(
            RiskFactor(
                factor_name="IMMEDIATE_RETRY_AFTER_DENIAL",
                score_addition=score,
                description="Purchase attempted within 30 minutes following a rejected transaction."
            )
        )

    # Factor 6: Online + Physical Channel Switching
    if pattern_result.online_pharmacy_accessed and pattern_result.distinct_pharmacies_24h >= 2:
        score = settings.RISK_WEIGHT_ONLINE_PHYSICAL_BURST
        total_score += score
        factors.append(
            RiskFactor(
                factor_name="HYBRID_CHANNEL_SWITCHING",
                score_addition=score,
                description="Cross-channel dispensing attempted across physical and online pharmacies."
            )
        )

    # Normalize total score between 0 and 100
    risk_score = min(100, max(0, total_score))

    # Map to Risk Level
    if risk_score <= settings.RISK_THRESHOLD_LOW_MAX:
        risk_level = "LOW"
        recommended_action = "APPROVE"
    elif risk_score <= settings.RISK_THRESHOLD_MEDIUM_MAX:
        risk_level = "MEDIUM"
        recommended_action = "PROCEED_WITH_LOG"
    elif risk_score <= settings.RISK_THRESHOLD_HIGH_MAX:
        risk_level = "HIGH"
        recommended_action = "HOLD_PHARMACIST_REVIEW"
    else:
        risk_level = "CRITICAL"
        recommended_action = "RESTRICT_CRITICAL_REVIEW"

    return RiskAgentResult(
        risk_score=risk_score,
        risk_level=risk_level,
        risk_factors=factors,
        recommended_action=recommended_action,
        timestamp=now
    )
