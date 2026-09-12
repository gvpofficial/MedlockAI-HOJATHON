import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.audit import log_audit_event
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.pharmacy import Pharmacy
from app.schemas.auth import UserRegister, UserLogin, Token, UserProfileResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token)
def register_user(req: UserRegister, db: Session = Depends(get_db)):
    # 1. Check if email already exists
    existing = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    role = req.role.upper().strip()
    if role not in ["PATIENT", "DOCTOR", "PHARMACY", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be PATIENT, DOCTOR, PHARMACY, or ADMIN."
        )

    # 2. Create User
    new_user = User(
        email=req.email.lower().strip(),
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name.strip(),
        role=role,
        phone=req.phone,
        is_active=True
    )
    db.add(new_user)
    db.flush()

    profile_id = None

    # 3. Create Specific Role Profile
    if role == "PATIENT":
        # Hash national ID if provided for privacy
        nat_hash = hashlib.sha256(req.phone.encode()).hexdigest() if req.phone else None
        patient = Patient(
            user_id=new_user.id,
            date_of_birth=req.date_of_birth,
            national_id_hash=nat_hash,
            emergency_contact=req.emergency_contact,
            blood_group=req.blood_group
        )
        db.add(patient)
        db.flush()
        profile_id = patient.id

    elif role == "DOCTOR":
        license_no = req.license_number or f"DOC-LIC-{new_user.id[:6].upper()}"
        doctor = Doctor(
            user_id=new_user.id,
            license_number=license_no,
            specialization=req.specialization or "General Medicine",
            hospital_clinic_name=req.hospital_clinic_name or "Metropolitan Medical Center",
            is_verified=True
        )
        db.add(doctor)
        db.flush()
        profile_id = doctor.id

    elif role == "PHARMACY":
        lic_no = req.license_number or f"PHARM-LIC-{new_user.id[:6].upper()}"
        pharmacy = Pharmacy(
            user_id=new_user.id,
            pharmacy_name=req.pharmacy_name or req.full_name,
            license_number=lic_no,
            pharmacy_type=req.pharmacy_type or "PHYSICAL_CHAIN",
            address=req.address or "100 Health Ave",
            is_active=True
        )
        db.add(pharmacy)
        db.flush()
        profile_id = pharmacy.id

    db.commit()
    db.refresh(new_user)

    # Audit log
    log_audit_event(
        db=db,
        event_type="USER_REGISTERED",
        target_entity="users",
        target_id=new_user.id,
        actor_user_id=new_user.id,
        actor_role=role,
        details={"email": new_user.email, "role": role, "profile_id": profile_id}
    )

    # Issue JWT token
    token = create_access_token(
        data={"sub": new_user.id, "email": new_user.email, "role": new_user.role, "profile_id": profile_id}
    )

    return Token(
        access_token=token,
        token_type="bearer",
        user_id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        role=new_user.role,
        profile_id=profile_id
    )


@router.post("/login", response_model=Token)
def login_user(req: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower().strip()).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is disabled. Contact system administrator."
        )

    profile_id = None
    if user.role == "PATIENT" and user.patient_profile:
        profile_id = user.patient_profile.id
    elif user.role == "DOCTOR" and user.doctor_profile:
        profile_id = user.doctor_profile.id
    elif user.role == "PHARMACY" and user.pharmacy_profile:
        profile_id = user.pharmacy_profile.id

    token = create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role, "profile_id": profile_id}
    )

    log_audit_event(
        db=db,
        event_type="USER_LOGIN",
        target_entity="users",
        target_id=user.id,
        actor_user_id=user.id,
        actor_role=user.role,
        details={"email": user.email}
    )

    return Token(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        profile_id=profile_id
    )


@router.get("/me", response_model=UserProfileResponse)
def get_current_user_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile_id = None
    profile_data = {}
    
    if user.role == "PATIENT" and user.patient_profile:
        profile_id = user.patient_profile.id
        profile_data = {
            "dob": str(user.patient_profile.date_of_birth) if user.patient_profile.date_of_birth else None,
            "emergency_contact": user.patient_profile.emergency_contact,
            "blood_group": user.patient_profile.blood_group
        }
    elif user.role == "DOCTOR" and user.doctor_profile:
        profile_id = user.doctor_profile.id
        profile_data = {
            "license_number": user.doctor_profile.license_number,
            "specialization": user.doctor_profile.specialization,
            "hospital": user.doctor_profile.hospital_clinic_name
        }
    elif user.role == "PHARMACY" and user.pharmacy_profile:
        profile_id = user.pharmacy_profile.id
        profile_data = {
            "pharmacy_name": user.pharmacy_profile.pharmacy_name,
            "license_number": user.pharmacy_profile.license_number,
            "pharmacy_type": user.pharmacy_profile.pharmacy_type,
            "address": user.pharmacy_profile.address
        }

    return UserProfileResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        phone=user.phone,
        is_active=user.is_active,
        created_at=user.created_at,
        profile_id=profile_id,
        profile_data=profile_data
    )
