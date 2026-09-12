# MEDLOCK AI — Hackathon Demo Scenarios Guide

This document details the 4 core demonstration scenarios pre-configured in MedLock AI.

---

## Scenario 1: Normal Authorized Purchase

- **Patient:** Johnathan Doe
- **Prescription Code:** `RX-2026-DEMO1`
- **Prescribed Item:** Demo Restricted Medicine X
- **Authorized Quantity:** 30 tablets
- **Previously Dispensed:** 0 tablets
- **Remaining Authorized:** 30 tablets
- **Pharmacy:** HealthFirst Pharmacy - Metro Branch
- **Requested Quantity:** 10 tablets
- **Evaluation & Outcome:**
  - Agent 1: Prescription `ACTIVE`, valid expiry, doctor and patient verified.
  - Agent 2: Requested 10 ≤ Remaining 30. `allowed: true`.
  - Agent 3: First provider visited today. No velocity anomalies.
  - Agent 4: Risk Score = 0 (`LOW`). Recommended Action: `APPROVE`.
  - Agent 5: Routine dispensing summary generated.
  - Decision: **`APPROVED`** (New remaining balance: 20 tablets).

---

## Scenario 2: Partial Cross-Pharmacy Refill

- **Patient:** Johnathan Doe
- **Prescription Code:** `RX-2026-DEMO1`
- **Prescribed Item:** Demo Restricted Medicine X
- **Authorized Quantity:** 30 tablets
- **Previously Dispensed:** 10 tablets (from Scenario 1)
- **Remaining Authorized:** 20 tablets
- **Pharmacy:** CarePlus Downtown Pharmacy *(Different participating pharmacy!)*
- **Requested Quantity:** 10 tablets
- **Evaluation & Outcome:**
  - Agent 1: Verified `ACTIVE`.
  - Agent 2: Checks central ledger. Total dispensed across network = 10. Remaining = 20. Requested 10 ≤ 20. `allowed: true`.
  - Agent 3: Normal interval between refills.
  - Agent 4: Risk Score = 0 (`LOW`).
  - Decision: **`APPROVED`** (New remaining balance: 10 tablets).

---

## Scenario 3: Deterministic Over-Quantity Denial

- **Patient:** Sarah Jenkins
- **Prescription Code:** `RX-2026-DEMO2`
- **Prescribed Item:** Oxycodone Controlled 10mg
- **Authorized Quantity:** 40 tablets
- **Previously Dispensed:** 30 tablets
- **Remaining Authorized:** 10 tablets
- **Pharmacy:** CVS Pharmacy Union Square
- **Requested Quantity:** 20 tablets *(Attempting 10 tablets in excess of balance)*
- **Evaluation & Outcome:**
  - Agent 1: Prescription is active.
  - Agent 2: Requested 20 > Remaining 10. `allowed: false`. Max permissible = 10.
  - Agent 4: Penalty applied (+25 points for excess request).
  - Decision: **`REJECTED`** with exact reason: *"Requested quantity (20) exceeds remaining authorized quantity (10)."*
  - Safety Note: Zero medicine dispensed. Patient received excess quantity warning.

---

## Scenario 4: Rapid Multi-Provider Activity Anomaly Hold

- **Patient:** David Miller
- **Prescription Code:** `RX-2026-DEMO3`
- **Prescribed Item:** Modafinil 200mg
- **Recent Network Activity:**
  - 10:15 → Metro Pharmacy (10 tablets approved)
  - 11:00 → CarePlus Downtown (10 tablets approved)
  - 11:30 → MedDirect Express Online (30 tablets requested, rejected)
  - 11:45 → Walgreens 42nd St (15 tablets requested)
- **Evaluation & Outcome:**
  - Agent 1: Verified `ACTIVE`.
  - Agent 2: Remaining balance is 40. Requested is 15 (arithmetic check alone passes).
  - Agent 3: Anomaly Detected! 3 distinct pharmacies visited in < 2 hours + online/physical alternation + immediate retry within 30 min of rejection.
  - Agent 4: Risk Score = **85 / 100 (`HIGH / CRITICAL`)**.
  - Agent 5: Clinical LLM synthesis: *"Patient attempted purchases at 3 distinct providers in 2 hours with a recent rejection. High velocity requires pharmacist verification."*
  - Decision: **`ON_HOLD` / `PHARMACIST_REVIEW_REQUIRED`**.
  - Escalation: Automatically opens a case in the Admin / Reviewer triage queue with patient notification.
