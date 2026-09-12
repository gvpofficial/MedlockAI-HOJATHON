# 🏛️ MEDLOCK AI — System Architecture & Design

This document details the architectural principles, component interactions, data flows, and security model of **MEDLOCK AI**.

---

## 1. System Architecture Diagram

```mermaid
flowchart TD
    subgraph ClientLayer["🖥️ Presentation Layer (Next.js 14 + Tailwind CSS + Lucide)"]
        Landing["Public Landing & Overview (/page.tsx)"]
        PatientUI["Patient Portal (/patient)"]
        DoctorUI["Doctor Portal (/doctor)"]
        PharmacyUI["Pharmacy Dispensing Portal (/pharmacy)"]
        AdminUI["Admin & Reviewer Portal (/admin)"]
        JudgeArena["Judge Demo Arena (/demo)"]
        TimelineUI["AI Decision Timeline Component"]
    end

    subgraph APILayer["⚡ API Gateway (FastAPI v1)"]
        AuthRouter["/api/v1/auth (JWT & RBAC)"]
        PrescriptionRouter["/api/v1/prescriptions (CRUD & QR)"]
        DispensingRouter["/api/v1/dispense (Verify, Evaluate & Execute)"]
        ReviewRouter["/api/v1/reviews (HITL Cases & Audits)"]
        DashboardRouter["/api/v1/dashboard (Aggregations)"]
        DemoRouter["/api/v1/demo (Scenario Triggers)"]
    end

    subgraph SecurityLayer["🛡️ Security & Zero-Trust Layer"]
        JWTMiddleware["JWT Authentication & RoleChecker"]
        DataSanitizer["Input Validation (Pydantic v2)"]
        AuditChaining["Tamper-Evident SHA-256 Chained Logger"]
    end

    subgraph AgentPipeline["🤖 Multi-Agent Orchestration Pipeline"]
        Orchestrator["Master Orchestrator (orchestrator.py)"]
        Agent1["Agent 1: Prescription Verification Agent"]
        Agent2["Agent 2: Dispensing Integrity Agent"]
        Agent3["Agent 3: Cross-Pharmacy Pattern Agent"]
        Agent4["Agent 4: Configurable Risk Engine"]
        Agent5["Agent 5: Review Summary Synthesizer"]
        DecisionGate["Central Decision Gate"]
    end

    subgraph StorageLayer["💾 Central Data & Ledger Storage"]
        PostgresDB[("Central PostgreSQL / SQLite Database")]
        AuditLedger[("Immutable SHA-256 Audit Log Chain")]
    end

    ClientLayer --> APILayer
    APILayer --> SecurityLayer
    SecurityLayer --> AgentPipeline
    AgentPipeline --> DecisionGate
    DecisionGate --> StorageLayer
    AuditChaining --> StorageLayer
```

---

## 2. End-to-End Dispensing Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Pharmacist as 👨‍⚕️ Pharmacy Terminal
    participant API as ⚡ Dispense API Gateway
    participant Agent1 as 🔍 Agent 1: Prescription Verification
    participant Agent2 as ⚖️ Agent 2: Dispensing Integrity
    participant Agent3 as 🌐 Agent 3: Cross-Pharmacy Pattern
    participant Agent4 as 🎯 Agent 4: Risk Engine
    participant Agent5 as 📝 Agent 5: Review Summary LLM
    participant DB as 💾 Central Database & Ledger
    participant Audit as 🔒 SHA-256 Audit Logger
    participant ReviewQueue as 🚨 Triage Review Queue

    Pharmacist->>API: POST /api/v1/dispense/execute (Rx Code, Medicine, Qty, Pharmacy ID)
    
    Note over API,Agent1: Step 1: Deterministic Prescription Verification
    API->>Agent1: Run Verification (Status, Expiry, Doctor, Patient, Medicine Code)
    Agent1->>DB: Query Prescription Record
    DB-->>Agent1: Return Prescription Record
    Agent1-->>API: VerificationResult { valid: true, status: "ACTIVE" }

    alt If Prescription is Expired, Cancelled, or Not Found
        API->>Audit: Log DISPENSING_REJECTED event
        API-->>Pharmacist: Reject Immediately with Rejection Reason
    end

    Note over API,Agent2: Step 2: Deterministic Central Ledger Calculation
    API->>Agent2: Compute Remaining Quantity from Central History
    Agent2->>DB: Sum all prior APPROVED / PARTIALLY_APPROVED transactions
    DB-->>Agent2: Total Dispensed: 20, Authorized: 30
    Agent2-->>API: IntegrityResult { remaining: 10, requested: 15, allowed: false }

    Note over API,Agent3: Step 3: Cross-Pharmacy Pattern & Anomaly Detection
    API->>Agent3: Scan 24h & 2h Central Activity across All Network Pharmacies
    Agent3->>DB: Fetch transactions & purchase attempts
    DB-->>Agent3: 3 distinct pharmacies visited in 2h + 1 recent online rejection
    Agent3-->>API: PatternResult { rapid_switching: true, distinct_2h: 3, rejections: 1 }

    Note over API,Agent4: Step 4: Transparent Risk Scoring Engine
    API->>Agent4: Evaluate Scored Penalties (Exceeds Qty: +25, Rapid Switching: +25, Rejection Burst: +30)
    Agent4-->>API: RiskResult { score: 85, level: "HIGH", factors: [...] }

    Note over API,Agent5: Step 5: Grounded Review Summary Generation
    API->>Agent5: Synthesize Clinical Briefing based strictly on Agents 1-4 evidence
    Agent5-->>API: Summary: "Patient attempted 3 purchases across physical & online providers in 2 hours..."

    Note over API,DB: Step 6: Central Decision Gate
    alt Disposition: APPROVED (Low Risk & Qty within Limits)
        API->>DB: Atomically commit transaction & decrement balance
        API->>Audit: Log DISPENSING_APPROVED (SHA-256 chained)
        API-->>Pharmacist: Return APPROVED + New Balance Receipt
    else Disposition: REJECTED (Zero remaining or hard constraint breach)
        API->>DB: Record REJECTED transaction & purchase attempt
        API->>DB: Create Patient Warning Notification
        API->>Audit: Log DISPENSING_REJECTED (SHA-256 chained)
        API-->>Pharmacist: Return REJECTED with exact arithmetic reason
    else Disposition: ON_HOLD / PHARMACIST_REVIEW_REQUIRED (High / Critical Risk)
        API->>DB: Record transaction as ON_HOLD
        API->>ReviewQueue: Create Triage Review Case
        API->>DB: Create Patient Safety Notice
        API->>Audit: Log DISPENSING_ON_HOLD (SHA-256 chained)
        API-->>Pharmacist: Return ON_HOLD + Escalation Case Reference
    end
```

---

## 3. Core Architectural Principles

### 1. Separation of Deterministic Rules from AI Reasoning
- **Hard Rules:** Mathematical limits, prescription validity dates, license validations, and quantity deductions are executed via deterministic code and relational database queries.
- **AI Role:** AI agents analyze behavioral velocity, provider hopping, channel switching, score risk transparently, and generate natural language summaries for clinicians. An LLM **never** determines quantity allowance.

### 2. Zero-Trust Central Dispensing Ledger
Every participating pharmacy (physical chain, independent, or online) queries the central ledger dynamically. No pharmacy relies on local cache or patient self-declaration.

### 3. Human-In-The-Loop (HITL) Guardrails
High-risk cases (Risk Score $\ge 50$) trigger an automated hold state. Automated dispensing is suspended, and the case is queued in the Admin / Reviewer portal for clinical override (`APPROVED_OVERRIDE`, `CONFIRMED_FRAUD`, `DISMISSED`).

### 4. Cryptographic Chained Audit Logging
To prevent audit log tampering, each log record contains:
$$\text{sha256\_hash} = \text{SHA-256}(\text{prev\_hash} \parallel \text{timestamp} \parallel \text{event\_type} \parallel \text{actor\_user\_id} \parallel \text{target\_entity} \parallel \text{details\_json})$$
This guarantees an immutable tamper-evident chain from the genesis block onward.
