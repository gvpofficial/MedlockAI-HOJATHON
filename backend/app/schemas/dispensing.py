from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schemas.agent import MultiAgentEvaluationResult


class DispenseVerifyRequest(BaseModel):
    prescription_code: str


class DispenseEvaluateRequest(BaseModel):
    prescription_code: str
    prescription_item_id: Optional[str] = None
    medicine_name: Optional[str] = None
    requested_quantity: int
    pharmacy_id: Optional[str] = None


class DispenseExecuteRequest(BaseModel):
    prescription_code: str
    prescription_item_id: Optional[str] = None
    medicine_name: Optional[str] = None
    requested_quantity: int
    pharmacy_id: Optional[str] = None


class DispensingTransactionResponse(BaseModel):
    id: str
    prescription_id: str
    prescription_code: Optional[str] = None
    prescription_item_id: str
    medicine_name: Optional[str] = None
    pharmacy_id: str
    pharmacy_name: Optional[str] = None
    requested_quantity: int
    approved_quantity: int
    remaining_before: int
    remaining_after: int
    status: str
    rejection_reason: Optional[str] = None
    transaction_timestamp: datetime
    integrity_hash: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DispenseExecuteResponse(BaseModel):
    transaction_id: Optional[str] = None
    decision: str
    message: str
    remaining_quantity: int
    evaluation: MultiAgentEvaluationResult
