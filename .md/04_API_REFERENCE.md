# 🔌 MEDLOCK AI — Complete REST API Reference

The MEDLOCK AI backend runs on FastAPI and exposes a comprehensive RESTful API under the prefix `/api/v1`.
Interactive Swagger UI documentation is available at `http://localhost:8000/docs`.

---

## Base Configuration

- **Default Base URL:** `http://localhost:8000/api/v1`
- **Authentication:** Bearer Token via HTTP Header: `Authorization: Bearer <JWT_TOKEN>`
- **Content-Type:** `application/json`

---

## 1. Authentication & Profiles (`/auth`)

### `POST /auth/register`
Creates a new user and role-specific profile (`PATIENT`, `DOCTOR`, `PHARMACY`, `ADMIN`).

**Request Body:**
```json
{
  "email": "sarah.j@patient.com",
  "password": "password123",
  "full_name": "Sarah Jenkins",
  "role": "PATIENT",
  "phone": "+1-555-0302",
  "date_of_birth": "1992-11-20",
  "emergency_contact": "+1-555-9999",
  "blood_group": "A+"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "token_type": "bearer",
  "user_id": "9f65c92b-8a21-4f32-bb17-10c9d92138e0",
  "email": "sarah.j@patient.com",
  "full_name": "Sarah Jenkins",
  "role": "PATIENT",
  "profile_id": "45d19a2e-7cb3-4819-86cb-b8efd880491a"
}
```

---

### `POST /auth/login`
Authenticates email and password, issuing a signed JWT access token.

**Request Body:**
```json
{
  "email": "doctor.vance@medlock.ai",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5...",
  "token_type": "bearer",
  "user_id": "84c1b920-1a2b-4c3d-8e9f-0123456789ab",
  "email": "doctor.vance@medlock.ai",
  "full_name": "Dr. Arthur Vance, MD",
  "role": "DOCTOR",
  "profile_id": "doc_profile_uuid"
}
```

---

### `GET /auth/me`
Retrieves authenticated user profile metadata and associated medical/pharmacy credentials.

---

## 2. Prescriptions (`/prescriptions`)

### `POST /prescriptions`
*(Requires `DOCTOR` or `ADMIN` role)*
Digitally creates and signs a new prescription with authorized quantities and QR payload.

**Request Body:**
```json
{
  "patient_id": "patient_uuid",
  "expiry_days": 30,
  "notes": "Restricted analgesic therapy. 1 tablet every 8 hours as needed.",
  "items": [
    {
      "medicine_name": "Demo Restricted Medicine X",
      "medicine_code": "NDC-MEDX-500",
      "is_restricted": true,
      "authorized_quantity": 30,
      "dosage_instructions": "1 tablet orally every 8 hours"
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "id": "rx_uuid",
  "prescription_code": "RX-2026-8942A",
  "patient_id": "patient_uuid",
  "patient_name": "Johnathan Doe",
  "doctor_id": "doctor_uuid",
  "doctor_name": "Dr. Arthur Vance, MD",
  "hospital_name": "Metropolitan General Hospital",
  "issue_date": "2026-09-12T10:00:00Z",
  "expiry_date": "2026-10-12T10:00:00Z",
  "status": "ACTIVE",
  "qr_code_data": "data:image/png;base64,iVBORw0KGgo...",
  "digital_signature": "SIG-SHA256-84920A...",
  "notes": "Restricted analgesic therapy.",
  "items": [
    {
      "id": "item_uuid",
      "medicine_name": "Demo Restricted Medicine X",
      "medicine_code": "NDC-MEDX-500",
      "is_restricted": true,
      "authorized_quantity": 30,
      "remaining_quantity": 30,
      "dosage_instructions": "1 tablet orally every 8 hours"
    }
  ]
}
```

---

### `GET /prescriptions`
Lists prescriptions filtered by the authenticated user's role (Patients view their own; Doctors view those they prescribed; Pharmacies/Admins view all).

---

### `GET /prescriptions/code/{code}`
Looks up a prescription by its human-readable code (e.g. `RX-2026-DEMO1`) or parsed QR payload. Dynamically computes the latest central ledger remaining quantity.

---

### `POST /prescriptions/{id}/cancel`
*(Requires `DOCTOR` or `ADMIN` role)*
Revokes and cancels a prescription. Changes status to `CANCELLED` and writes an audit log.

---

## 3. Dispensing & Multi-Agent Engine (`/dispense`)

### `POST /dispense/evaluate`
**Dry-run evaluation.** Runs Agents 1 through 5 and produces the complete 6-step `DecisionTimelineStep` array, transparent risk score, and clinical summary **without** writing changes to the database.

**Request Body:**
```json
{
  "prescription_code": "RX-2026-DEMO1",
  "requested_quantity": 10,
  "pharmacy_id": "pharmacy_uuid"
}
```

**Response (200 OK):** Returns `MultiAgentEvaluationResult` containing:
- `decision`: `APPROVED`, `PARTIALLY_APPROVED`, `REJECTED`, or `ON_HOLD`
- `risk_score`: Integer `0 - 100`
- `risk_level`: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- `verification`: Agent 1 structured result
- `integrity`: Agent 2 ledger arithmetic result
- `pattern`: Agent 3 velocity & burst detection result
- `risk`: Agent 4 scored factors breakdown
- `summary`: Agent 5 clinical briefing
- `timeline`: Array of 6 sequential steps for UI visualization

---

### `POST /dispense/execute`
*(Requires `PHARMACY` or `ADMIN` role)*
**Commits the transaction.** Executes the multi-agent pipeline, writes to `dispensing_transactions`, decrements remaining balance atomically, creates `purchase_attempts`, generates `risk_events` and `review_cases` if on hold, and appends a cryptographically chained SHA-256 record to `audit_logs`.

**Request Body:**
```json
{
  "prescription_code": "RX-2026-DEMO1",
  "requested_quantity": 10,
  "pharmacy_id": "pharmacy_uuid"
}
```

**Response (200 OK):**
```json
{
  "transaction_id": "tx_uuid",
  "decision": "APPROVED",
  "message": "Dispensing approved successfully for 10 units of Demo Restricted Medicine X.",
  "remaining_quantity": 20,
  "evaluation": { ... }
}
```

---

### `GET /dispense/history`
Returns historical dispensing transactions filtered by prescription or pharmacy.

---

## 4. Reviews, Triage & Audit (`/reviews`)

### `GET /reviews/cases`
*(Requires `ADMIN`, `PHARMACY`, or `DOCTOR` role)*
Returns triage review cases filtered optionally by `?status_filter=PENDING`.

---

### `GET /reviews/cases/{id}`
Returns details of a specific triage case with evidence summary and associated prescription.

---

### `POST /reviews/cases/{id}/resolve`
*(Requires `ADMIN` or `PHARMACY` role)*
Commits a human clinician resolution on a held transaction.

**Request Body:**
```json
{
  "resolution": "APPROVED_OVERRIDE",
  "reviewer_notes": "Verified post-operative prescription requirement with Dr. Vance. Authorized release of medication."
}
```
*Valid resolutions:* `APPROVED_OVERRIDE`, `CONFIRMED_FRAUD`, `DISMISSED`.

---

### `GET /reviews/audit-logs`
*(Requires `ADMIN` or `PHARMACY` role)*
Returns immutable cryptographic audit log entries with previous block hash, current SHA-256 hash, and event payload.

---

### `GET /reviews/warnings`
Returns active safety warnings and held transaction notices for the authenticated patient.

---

### `GET /reviews/stats`
Returns high-level system telemetry:
- `total_prescriptions`
- `active_prescriptions`
- `total_dispensing_transactions`
- `prevented_excess_dispenses`
- `pending_review_cases`
- `active_pharmacies`

---

## 5. Dashboards (`/dashboard`)

- `GET /dashboard/patient`: Aggregated patient cards, prescription gauges, warnings, and dispensing logs.
- `GET /dashboard/doctor`: Doctor metrics, issued prescriptions, and patient selector dropdown.
- `GET /dashboard/pharmacy`: Pharmacy metrics, branch selector, and recent terminal transactions.

---

## 6. Demo & Scenarios (`/demo`)

- `POST /demo/reset-seed`: Resets database and reseeds 5 patients, 2 doctors, 5 pharmacies, and all 5 test prescriptions.
- `GET /demo/scenarios`: Returns metadata for Scenarios 1, 2, 3, and 4.
- `POST /demo/scenarios/{scenario_id}/execute`: Triggers immediate live evaluation of the specified scenario.
