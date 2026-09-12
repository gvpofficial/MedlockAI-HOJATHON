from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str  # PATIENT, DOCTOR, PHARMACY, ADMIN
    phone: Optional[str] = None
    
    # Optional Profile Specific Fields
    date_of_birth: Optional[date] = None
    emergency_contact: Optional[str] = None
    blood_group: Optional[str] = None
    
    license_number: Optional[str] = None
    specialization: Optional[str] = None
    hospital_clinic_name: Optional[str] = None
    
    pharmacy_name: Optional[str] = None
    pharmacy_type: Optional[str] = "PHYSICAL_CHAIN"  # PHYSICAL_CHAIN, INDEPENDENT, ONLINE
    address: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str
    role: str
    profile_id: Optional[str] = None


class UserProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    phone: Optional[str] = None
    is_active: bool
    created_at: datetime
    profile_id: Optional[str] = None
    profile_data: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)
