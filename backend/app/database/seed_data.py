from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.core.prescription_utils import (
    generate_digital_signature,
    generate_qr_code_base64
)
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.pharmacy import Pharmacy
from app.models.prescription import Prescription, PrescriptionItem
from app.models.dispensing import DispensingTransaction, PurchaseAttempt
from app.models.risk import RiskEvent, Warning
from app.models.review import ReviewCase
from app.models.audit import AuditLog


def seed_database(db: Session):
    # Check if database is already populated
    if db.query(User).count() > 0:
        return

    now = datetime.now(timezone.utc)
    hashed_pwd = get_password_hash("password123")

    # 1. CREATE ADMIN
    admin_user = User(
        email="admin@medlock.ai",
        hashed_password=hashed_pwd,
        full_name="Dr. Eleanor Vance (System Admin)",
        role="ADMIN",
        phone="+1-555-0100",
        is_active=True
    )
    db.add(admin_user)

    # 2. CREATE DOCTORS
    doc1_user = User(
        email="doctor.vance@medlock.ai",
        hashed_password=hashed_pwd,
        full_name="Dr. Arthur Vance, MD",
        role="DOCTOR",
        phone="+1-555-0101",
        is_active=True
    )
    doc2_user = User(
        email="doctor.rostova@medlock.ai",
        hashed_password=hashed_pwd,
        full_name="Dr. Elena Rostova, MD",
        role="DOCTOR",
        phone="+1-555-0102",
        is_active=True
    )
    db.add_all([doc1_user, doc2_user])
    db.flush()

    doc1 = Doctor(
        user_id=doc1_user.id,
        license_number="MD-NY-84920",
        specialization="Pain Management & Neurology",
        hospital_clinic_name="Metropolitan General Hospital",
        is_verified=True
    )
    doc2 = Doctor(
        user_id=doc2_user.id,
        license_number="MD-NY-77312",
        specialization="Internal Medicine & Psychiatry",
        hospital_clinic_name="St. Jude Medical Pavilion",
        is_verified=True
    )
    db.add_all([doc1, doc2])
    db.flush()

    # 3. CREATE PHARMACIES (4 Physical + 1 Online)
    pharm_users = [
        ("metro@pharmacy.com", "HealthFirst Pharmacy - Metro Branch", "PHYSICAL_CHAIN", "101 Broadway Ave, New York, NY", "PHARM-LIC-001"),
        ("careplus@pharmacy.com", "CarePlus Downtown Pharmacy", "PHYSICAL_CHAIN", "450 5th Avenue, New York, NY", "PHARM-LIC-002"),
        ("walgreens42@pharmacy.com", "Walgreens 42nd St", "PHYSICAL_CHAIN", "200 W 42nd St, New York, NY", "PHARM-LIC-003"),
        ("cvsunion@pharmacy.com", "CVS Pharmacy Union Square", "INDEPENDENT", "14 Union Square East, New York, NY", "PHARM-LIC-004"),
        ("express@onlinepharmacy.com", "MedDirect Express Online Rx", "ONLINE", "https://meddirect-express.com", "PHARM-LIC-ONLINE-001"),
    ]

    pharmacies = []
    for email, name, ptype, addr, lic in pharm_users:
        u = User(
            email=email,
            hashed_password=hashed_pwd,
            full_name=name,
            role="PHARMACY",
            phone="+1-555-0200",
            is_active=True
        )
        db.add(u)
        db.flush()
        p = Pharmacy(
            user_id=u.id,
            pharmacy_name=name,
            license_number=lic,
            pharmacy_type=ptype,
            address=addr,
            is_active=True
        )
        db.add(p)
        pharmacies.append(p)
    db.flush()

    # 4. CREATE PATIENTS (5 Patients)
    patient_data = [
        ("john.doe@patient.com", "Johnathan Doe", "1988-05-14", "O+", "+1-555-0301"),
        ("sarah.j@patient.com", "Sarah Jenkins", "1992-11-20", "A+", "+1-555-0302"),
        ("david.m@patient.com", "David Miller", "1975-03-08", "B-", "+1-555-0303"),
        ("emma.w@patient.com", "Emma Watson", "1995-07-25", "AB+", "+1-555-0304"),
        ("michael.c@patient.com", "Michael Chang", "1982-09-30", "O-", "+1-555-0305"),
    ]

    patients = []
    for email, name, dob_str, bgroup, phone in patient_data:
        u = User(
            email=email,
            hashed_password=hashed_pwd,
            full_name=name,
            role="PATIENT",
            phone=phone,
            is_active=True
        )
        db.add(u)
        db.flush()
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        pat = Patient(
            user_id=u.id,
            date_of_birth=dob,
            blood_group=bgroup,
            emergency_contact="+1-555-9999"
        )
        db.add(pat)
        patients.append(pat)
    db.flush()

    # 5. CREATE SEED PRESCRIPTIONS
    # Rx 1: John Doe - Demo Restricted Medicine X (30 tabs)
    code1 = "RX-2026-DEMO1"
    qr1 = generate_qr_code_base64(f"MEDLOCK_RX:{code1}:{patients[0].id}:SIG001")
    rx1 = Prescription(
        prescription_code=code1,
        patient_id=patients[0].id,
        doctor_id=doc1.id,
        issue_date=now - timedelta(days=2),
        expiry_date=now + timedelta(days=28),
        status="ACTIVE",
        qr_code_data=qr1,
        digital_signature="SIG-SHA256-VANCE-DEMO1",
        notes="Restricted analgesic therapy. 1 tablet every 8 hours as needed."
    )
    db.add(rx1)
    db.flush()
    item1 = PrescriptionItem(
        prescription_id=rx1.id,
        medicine_name="Demo Restricted Medicine X",
        medicine_code="NDC-MEDX-500",
        is_restricted=True,
        authorized_quantity=30,
        remaining_quantity=30,
        dosage_instructions="10mg tablet orally every 8 hours"
    )
    db.add(item1)

    # Rx 2: Sarah Jenkins - Oxycodone Controlled 10mg (40 tabs, 30 dispensed, 10 remaining)
    code2 = "RX-2026-DEMO2"
    qr2 = generate_qr_code_base64(f"MEDLOCK_RX:{code2}:{patients[1].id}:SIG002")
    rx2 = Prescription(
        prescription_code=code2,
        patient_id=patients[1].id,
        doctor_id=doc1.id,
        issue_date=now - timedelta(days=10),
        expiry_date=now + timedelta(days=20),
        status="ACTIVE",
        qr_code_data=qr2,
        digital_signature="SIG-SHA256-VANCE-DEMO2",
        notes="Post-surgical recovery. Take with food."
    )
    db.add(rx2)
    db.flush()
    item2 = PrescriptionItem(
        prescription_id=rx2.id,
        medicine_name="Oxycodone Controlled 10mg",
        medicine_code="NDC-OXYC-10MG",
        is_restricted=True,
        authorized_quantity=40,
        remaining_quantity=10,
        dosage_instructions="1 tablet every 6 hours"
    )
    db.add(item2)
    db.flush()

    # Seed prior transaction for Rx 2: 30 tablets already dispensed at Metro Pharmacy
    tx_prior_rx2 = DispensingTransaction(
        prescription_id=rx2.id,
        prescription_item_id=item2.id,
        pharmacy_id=pharmacies[0].id,
        requested_quantity=30,
        approved_quantity=30,
        remaining_before=40,
        remaining_after=10,
        status="APPROVED",
        transaction_timestamp=now - timedelta(days=5),
        integrity_hash="HASH_SEED_TX_002"
    )
    db.add(tx_prior_rx2)

    # Rx 3: David Miller - Modafinil 200mg (60 tabs) with rapid burst history
    code3 = "RX-2026-DEMO3"
    qr3 = generate_qr_code_base64(f"MEDLOCK_RX:{code3}:{patients[2].id}:SIG003")
    rx3 = Prescription(
        prescription_code=code3,
        patient_id=patients[2].id,
        doctor_id=doc2.id,
        issue_date=now - timedelta(days=1),
        expiry_date=now + timedelta(days=29),
        status="ACTIVE",
        qr_code_data=qr3,
        digital_signature="SIG-SHA256-ROSTOVA-DEMO3",
        notes="Narcolepsy management."
    )
    db.add(rx3)
    db.flush()
    item3 = PrescriptionItem(
        prescription_id=rx3.id,
        medicine_name="Modafinil 200mg",
        medicine_code="NDC-MODA-200",
        is_restricted=True,
        authorized_quantity=60,
        remaining_quantity=40,
        dosage_instructions="1 tablet each morning"
    )
    db.add(item3)
    db.flush()

    # Seed rapid multi-provider purchase attempts for Rx 3
    # 1. Metro Pharmacy -> 10 approved (1.5 hours ago)
    tx_burst1 = DispensingTransaction(
        prescription_id=rx3.id,
        prescription_item_id=item3.id,
        pharmacy_id=pharmacies[0].id,
        requested_quantity=10,
        approved_quantity=10,
        remaining_before=60,
        remaining_after=50,
        status="APPROVED",
        transaction_timestamp=now - timedelta(hours=1, minutes=45),
        integrity_hash="HASH_BURST_1"
    )
    # 2. CarePlus Downtown -> 10 approved (1 hour ago)
    tx_burst2 = DispensingTransaction(
        prescription_id=rx3.id,
        prescription_item_id=item3.id,
        pharmacy_id=pharmacies[1].id,
        requested_quantity=10,
        approved_quantity=10,
        remaining_before=50,
        remaining_after=40,
        status="APPROVED",
        transaction_timestamp=now - timedelta(hours=1),
        integrity_hash="HASH_BURST_2"
    )
    # 3. Online Pharmacy -> 30 requested -> Rejected (30 min ago)
    att_burst3 = PurchaseAttempt(
        prescription_id=rx3.id,
        pharmacy_id=pharmacies[4].id,
        requested_quantity=30,
        attempt_timestamp=now - timedelta(minutes=15),
        outcome="REJECTED"
    )
    db.add_all([tx_burst1, tx_burst2, att_burst3])

    # Rx 4: Emma Watson - Zolpidem 10mg (30 tabs)
    code4 = "RX-2026-DEMO4"
    qr4 = generate_qr_code_base64(f"MEDLOCK_RX:{code4}:{patients[3].id}:SIG004")
    rx4 = Prescription(
        prescription_code=code4,
        patient_id=patients[3].id,
        doctor_id=doc2.id,
        issue_date=now - timedelta(days=3),
        expiry_date=now + timedelta(days=27),
        status="ACTIVE",
        qr_code_data=qr4,
        digital_signature="SIG-SHA256-ROSTOVA-DEMO4",
        notes="Insomnia treatment. Bedtime only."
    )
    db.add(rx4)
    db.flush()
    item4 = PrescriptionItem(
        prescription_id=rx4.id,
        medicine_name="Zolpidem 10mg",
        medicine_code="NDC-ZOLP-10MG",
        is_restricted=True,
        authorized_quantity=30,
        remaining_quantity=30,
        dosage_instructions="1 tablet before bed"
    )
    db.add(item4)

    # Rx 5: Michael Chang - Methylphenidate 20mg (50 tabs)
    code5 = "RX-2026-DEMO5"
    qr5 = generate_qr_code_base64(f"MEDLOCK_RX:{code5}:{patients[4].id}:SIG005")
    rx5 = Prescription(
        prescription_code=code5,
        patient_id=patients[4].id,
        doctor_id=doc1.id,
        issue_date=now - timedelta(days=4),
        expiry_date=now + timedelta(days=26),
        status="ACTIVE",
        qr_code_data=qr5,
        digital_signature="SIG-SHA256-VANCE-DEMO5",
        notes="ADHD management."
    )
    db.add(rx5)
    db.flush()
    item5 = PrescriptionItem(
        prescription_id=rx5.id,
        medicine_name="Methylphenidate 20mg",
        medicine_code="NDC-METH-20MG",
        is_restricted=True,
        authorized_quantity=50,
        remaining_quantity=50,
        dosage_instructions="1 tablet twice daily"
    )
    db.add(item5)

    # Genesis Audit Log
    db.commit()
