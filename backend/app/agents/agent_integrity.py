from datetime import datetime, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.dispensing import DispensingTransaction
from app.models.prescription import PrescriptionItem
from app.schemas.agent import IntegrityAgentResult


def run_dispensing_integrity_agent(
    db: Session,
    item: PrescriptionItem,
    requested_quantity: int
) -> IntegrityAgentResult:
    now = datetime.now(timezone.utc)
    
    # Deterministic query: Sum all prior approved and partially approved dispensing quantities
    dispensed_sum = (
        db.query(func.coalesce(func.sum(DispensingTransaction.approved_quantity), 0))
        .filter(
            DispensingTransaction.prescription_item_id == item.id,
            DispensingTransaction.status.in_(["APPROVED", "PARTIALLY_APPROVED"])
        )
        .scalar()
    ) or 0
    
    authorized_qty = item.authorized_quantity
    dispensed_qty = int(dispensed_sum)
    remaining_qty = max(0, authorized_qty - dispensed_qty)
    
    allowed = (requested_quantity <= remaining_qty) and (remaining_qty > 0)
    max_permissible = min(requested_quantity, remaining_qty)
    is_partial_possible = (remaining_qty > 0) and (requested_quantity > remaining_qty)
    
    reason = None
    if remaining_qty == 0:
        reason = f"Authorized quantity ({authorized_qty}) has been fully dispensed across prior transactions."
    elif requested_quantity > remaining_qty:
        reason = f"Requested quantity ({requested_quantity}) exceeds remaining authorized quantity ({remaining_qty})."
    else:
        reason = f"Quantity request ({requested_quantity}) is within remaining limit ({remaining_qty}/{authorized_qty})."

    return IntegrityAgentResult(
        item_id=item.id,
        medicine_name=item.medicine_name,
        authorized_quantity=authorized_qty,
        dispensed_quantity=dispensed_qty,
        remaining_quantity=remaining_qty,
        requested_quantity=requested_quantity,
        allowed=allowed,
        max_permissible_quantity=max_permissible,
        is_partial_possible=is_partial_possible,
        reason=reason,
        timestamp=now
    )
