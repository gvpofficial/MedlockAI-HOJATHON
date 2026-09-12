# 🧪 MEDLOCK AI — Demo Scenarios & Testing Suite Guide

This document details the pre-configured seed data fixtures, the 4 hackathon demo scenarios, and how to verify the system using automated test suites.

---

## 1. Pre-Configured Seed Data Fixtures

When the backend starts (or when `/demo/reset-seed` is called), the database is automatically seeded with:

### Patients (5)
1. **Johnathan Doe** (`john.doe@patient.com`) — DOB: 1988-05-14, Blood: `O+`
2. **Sarah Jenkins** (`sarah.j@patient.com`) — DOB: 1992-11-20, Blood: `A+`
3. **David Miller** (`david.m@patient.com`) — DOB: 1975-03-08, Blood: `B-`
4. **Emma Watson** (`emma.w@patient.com`) — DOB: 1995-07-25, Blood: `AB+`
5. **Michael Chang** (`michael.c@patient.com`) — DOB: 1982-09-30, Blood: `O-`

### Doctors (2)
1. **Dr. Arthur Vance, MD** (`doctor.vance@medlock.ai`) — License: `MD-NY-84920`, Pain Management, Metropolitan General Hospital
2. **Dr. Elena Rostova, MD** (`doctor.rostova@medlock.ai`) — License: `MD-NY-77312`, Psychiatry, St. Jude Medical Pavilion

### Participating Pharmacies (5: 4 Physical + 1 Online)
1. **HealthFirst Pharmacy - Metro Branch** (`metro@pharmacy.com`) — `PHYSICAL_CHAIN`
2. **CarePlus Downtown Pharmacy** (`careplus@pharmacy.com`) — `PHYSICAL_CHAIN`
3. **Walgreens 42nd St** (`walgreens42@pharmacy.com`) — `PHYSICAL_CHAIN`
4. **CVS Pharmacy Union Square** (`cvsunion@pharmacy.com`) — `INDEPENDENT`
5. **MedDirect Express Online Rx** (`express@onlinepharmacy.com`) — `ONLINE`

---

## 2. The 4 Hackathon Demo Scenarios

### 🟢 Scenario 1: Normal Authorized Purchase
- **Goal:** Demonstrate standard, legitimate first-time dispensing.
- **Trigger:** Request 10 tablets of *Demo Restricted Medicine X* on prescription `RX-2026-DEMO1` at **HealthFirst Metro**.
- **Prescription State:** Authorized: 30 | Previously Dispensed: 0 | Remaining: 30
- **Agent Execution:**
  - `Agent 1`: Verified `ACTIVE`, doctor verified, patient identity matched.
  - `Agent 2`: Requested 10 $\le$ Remaining 30. Allowed = `true`. Max permissible = 10.
  - `Agent 3`: Normal single-provider activity in 24h.
  - `Agent 4`: Risk Score = **`0 / 100 (LOW)`**.
  - `Agent 5`: Summary: Routine dispensing authorized.
- **Result:** **`APPROVED`**
- **Ledger Impact:** Remaining balance decreases from **30 to 20 tablets**.

---

### 🟢 Scenario 2: Partial Cross-Pharmacy Refill
- **Goal:** Prove cross-pharmacy central synchronization between different participating chains.
- **Trigger:** Following Scenario 1, the patient visits a **different** pharmacy (**CarePlus Downtown**) requesting 10 tablets on `RX-2026-DEMO1`.
- **Prescription State:** Authorized: 30 | Previously Dispensed: 10 | Remaining: 20
- **Agent Execution:**
  - `Agent 1`: Verified `ACTIVE`.
  - `Agent 2`: Checks central ledger. Detects prior 10 tablets dispensed at Metro. Remaining balance is 20. Requested 10 $\le$ Remaining 20. Allowed = `true`.
  - `Agent 3`: Normal refill interval.
  - `Agent 4`: Risk Score = **`0 / 100 (LOW)`**.
- **Result:** **`APPROVED`**
- **Ledger Impact:** Remaining balance decreases from **20 to 10 tablets**.

---

### 🔴 Scenario 3: Deterministic Over-Quantity Denial
- **Goal:** Prove that hard database rules prevent excess dispensing without relying on an LLM.
- **Trigger:** Sarah Jenkins visits **CVS Union Square** requesting 20 tablets of *Oxycodone Controlled 10mg* on prescription `RX-2026-DEMO2`.
- **Prescription State:** Authorized: 40 | Previously Dispensed: 30 | Remaining: 10
- **Agent Execution:**
  - `Agent 1`: Verified `ACTIVE`.
  - `Agent 2`: Requested 20 $>$ Remaining 10. Allowed = `false`. Flags `QUANTITY_EXCEEDS_REMAINING`.
  - `Agent 4`: Penalty applied (+25 points for excess request).
- **Result:** **`REJECTED`**
- **Exact Rejection Reason:** *"Requested quantity (20) exceeds remaining authorized quantity (10)."*
- **Safety Impact:** 0 tablets dispensed. Central balance remains 10. Safety warning sent to patient.

---

### 🟡 Scenario 4: Rapid Multi-Provider Activity Anomaly Hold
- **Goal:** Showcase the Agentic AI layer detecting rapid provider switching, online/physical hopping, and rejection bursts.
- **Trigger:** David Miller visits **Walgreens 42nd St** requesting 15 tablets of *Modafinil 200mg* on prescription `RX-2026-DEMO3`.
- **Prior Network Activity (in the last 2 hours):**
  1. 10:15 $\rightarrow$ Metro Pharmacy (10 tablets approved)
  2. 11:00 $\rightarrow$ CarePlus Downtown (10 tablets approved)
  3. 11:45 $\rightarrow$ MedDirect Express Online (30 tablets requested $\rightarrow$ Rejected)
  4. 12:00 $\rightarrow$ Walgreens 42nd St (15 tablets requested)
- **Agent Execution:**
  - `Agent 1`: Verified `ACTIVE`.
  - `Agent 2`: Ledger arithmetic alone: Requested 15 $\le$ Remaining 40 (passes arithmetic).
  - `Agent 3`: **Anomaly Detected!** 3 distinct pharmacies visited in $< 2$ hours + online/physical alternation + immediate retry within 30 minutes of denial.
  - `Agent 4`: Risk Score = **`90 / 100 (CRITICAL)`**
    - Rapid Provider Switching: `+25`
    - Repeated Rejections: `+20`
    - Immediate Retry After Denial: `+30`
    - Hybrid Channel Switching: `+15`
  - `Agent 5`: Grounded briefing formulated for the pharmacist: *"Within 2 hours, patient visited 4 distinct providers with an online rejection. High velocity requires pharmacist verification."*
- **Result:** **`ON_HOLD` / `PHARMACIST_REVIEW_REQUIRED`**
- **Escalation:** Creates case `CASE-2026-XXXX` in the Admin / Reviewer triage queue.

---

## 3. Automated Test Suite Execution

MEDLOCK AI includes unit and end-to-end integration tests in `backend/tests/`.

### Running All Tests
```powershell
python -m pytest -o pythonpath=backend backend/tests -v
```

### Verified Test Suite Roster
- `test_integrity_normal_allowance`: Verifies that Agent 2 correctly computes remaining quantities and approves valid requests.
- `test_integrity_excess_rejection`: Verifies that Agent 2 deterministically rejects requests exceeding remaining limits.
- `test_cross_pharmacy_burst_detection`: Verifies that Agent 3 and Agent 4 detect rapid switching ($< 2$h) and score risk $\ge 50$.
- `test_scenario_1_normal_purchase`: End-to-end execution of Scenario 1 (`APPROVED`).
- `test_scenario_2_partial_cross_pharmacy`: End-to-end execution of Scenario 2 (`APPROVED`).
- `test_scenario_3_over_quantity_denial`: End-to-end execution of Scenario 3 (`REJECTED`).
- `test_scenario_4_rapid_multi_provider_hold`: End-to-end execution of Scenario 4 (`ON_HOLD`).

**All 7 tests pass 100% with zero errors.**
