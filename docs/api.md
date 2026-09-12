# MEDLOCK AI — REST API Documentation

The MedLock AI backend exposes a RESTful API with automated Swagger OpenAPI documentation at `http://localhost:8000/docs`.

---

## Base URL
```
http://localhost:8000/api/v1
```

---

## 1. Authentication Endpoints (`/auth`)

### `POST /auth/register`
Registers a new user and creates their role-specific profile (`PATIENT`, `DOCTOR`, `PHARMACY`, `ADMIN`).

**Request Body:**
```json
{
  "email": "sarah.j@patient.com",
  "password": "password123",
  "full_name": "Sarah Jenkins",
  "role": "PATIENT",
  "phone": "+1-555-0302"
}
```

### `POST /auth/login`
Authenticates user credentials and returns a JWT access token.

**Response:**
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user_id": "9f65...",
  "email": "sarah.j@patient.com",
  "full_name": "Sarah Jenkins",
  "role": "PATIENT",
  "profile_id": "84c1..."
}
```

---

## 2. Prescription Endpoints (`/prescriptions`)

### `POST /prescriptions`
*(Requires DOCTOR or ADMIN role)*
Digitally creates a prescription with item limits, cryptographic signature, and Base64 QR code.

**Request Body:**
```json
{
  "patient_id": "84c1...",
  "expiry_days": 30,
  "notes": "Analgesic therapy.",
  "items": [
    {
      "medicine_name": "Oxycodone Controlled 10mg",
      "authorized_quantity": 40,
      "dosage_instructions": "1 tablet every 6 hours",
      "is_restricted": true
    }
  ]
}
```

### `GET /prescriptions/code/{code}`
Retrieves complete prescription details, including real-time remaining quantities queried dynamically from the central ledger.

---

## 3. Dispensing & Multi-Agent Evaluation (`/dispense`)

### `POST /dispense/evaluate`
Executes a dry-run of the full 5-agent pipeline without committing transactions to the database. Returns step-by-step timeline, transparent risk score, and clinical summary.

**Request Body:**
```json
{
  "prescription_code": "RX-2026-DEMO1",
  "requested_quantity": 10,
  "pharmacy_id": "pharm_id_1"
}
```

### `POST /dispense/execute`
*(Requires PHARMACY or ADMIN role)*
Executes and atomically commits the dispensing transaction to the centralized database ledger, updating balance and generating audit entries.

---

## 4. Review & Triage Endpoints (`/reviews`)

### `GET /reviews/cases`
Lists triage cases filtered by status (`PENDING`, `UNDER_REVIEW`, `APPROVED_OVERRIDE`, `CONFIRMED_FRAUD`, `DISMISSED`).

### `POST /reviews/cases/{id}/resolve`
*(Requires ADMIN or PHARMACY role)*
Commits a human reviewer decision (`APPROVED_OVERRIDE`, `CONFIRMED_FRAUD`, `DISMISSED`) with reviewer notes and logs audit trail.

### `GET /reviews/audit-logs`
Retrieves immutable SHA-256 cryptographic audit logs.

---

## 5. Demo Suite Endpoints (`/demo`)

### `POST /demo/reset-seed`
Resets the database and reseeds 5 patients, 2 doctors, 5 pharmacies, and all demo prescriptions.

### `POST /demo/scenarios/{scenario_id}/execute`
Executes Scenario 1, 2, 3, or 4 and returns full multi-agent evaluation output.
