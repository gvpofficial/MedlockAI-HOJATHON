export type Role = 'PATIENT' | 'DOCTOR' | 'PHARMACY' | 'ADMIN';

export interface UserSession {
  access_token: string;
  token_type: string;
  user_id: string;
  email: string;
  full_name: string;
  role: Role;
  profile_id?: string;
}

export interface PrescriptionItem {
  id: string;
  medicine_name: string;
  medicine_code?: string;
  is_restricted: boolean;
  authorized_quantity: number;
  remaining_quantity: number;
  dosage_instructions?: string;
  created_at?: string;
}

export interface Prescription {
  id: string;
  prescription_code: string;
  patient_id: string;
  patient_name?: string;
  doctor_id: string;
  doctor_name?: string;
  hospital_name?: string;
  issue_date: string;
  expiry_date: string;
  status: 'ACTIVE' | 'EXHAUSTED' | 'EXPIRED' | 'CANCELLED' | 'SUSPENDED';
  qr_code_data?: string;
  digital_signature?: string;
  notes?: string;
  items: PrescriptionItem[];
  created_at: string;
  updated_at?: string;
}

export interface VerificationAgentResult {
  agent_name: string;
  valid: boolean;
  prescription_id?: string;
  prescription_code?: string;
  prescription_status: string;
  expiry_valid: boolean;
  doctor_verified: boolean;
  patient_verified: boolean;
  medicine_match: boolean;
  rejection_reason?: string;
  timestamp: string;
}

export interface IntegrityAgentResult {
  agent_name: string;
  item_id?: string;
  medicine_name: string;
  authorized_quantity: number;
  dispensed_quantity: number;
  remaining_quantity: number;
  requested_quantity: number;
  allowed: boolean;
  max_permissible_quantity: number;
  is_partial_possible: boolean;
  reason?: string;
  timestamp: string;
}

export interface PatternAgentResult {
  agent_name: string;
  distinct_pharmacies_24h: number;
  distinct_pharmacies_2h: number;
  online_pharmacy_accessed: boolean;
  recent_rejected_attempts_48h: number;
  rapid_provider_switching_detected: boolean;
  burst_after_rejection_detected: boolean;
  anomaly_detected: boolean;
  pattern_reasons: string[];
  timestamp: string;
}

export interface RiskFactor {
  factor_name: string;
  score_addition: number;
  description: string;
}

export interface RiskAgentResult {
  agent_name: string;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  risk_factors: RiskFactor[];
  recommended_action: string;
  timestamp: string;
}

export interface SummaryAgentResult {
  agent_name: string;
  clinical_summary: string;
  key_evidence: string[];
  requires_human_review: boolean;
  timestamp: string;
}

export interface DecisionTimelineStep {
  step_number: number;
  agent_name: string;
  status: 'SUCCESS' | 'WARNING' | 'DANGER' | 'INFO';
  title: string;
  description: string;
  data: Record<string, any>;
}

export interface MultiAgentEvaluationResult {
  decision: 'APPROVED' | 'PARTIALLY_APPROVED' | 'REJECTED' | 'ON_HOLD' | 'PHARMACIST_REVIEW_REQUIRED';
  prescription_code: string;
  medicine_name: string;
  requested_quantity: number;
  approved_quantity: number;
  remaining_before: number;
  remaining_after: number;
  risk_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  verification: VerificationAgentResult;
  integrity: IntegrityAgentResult;
  pattern: PatternAgentResult;
  risk: RiskAgentResult;
  summary: SummaryAgentResult;
  timeline: DecisionTimelineStep[];
  requires_pharmacist_review: boolean;
  review_case_id?: string;
}

export interface DispenseExecuteResponse {
  transaction_id?: string;
  decision: string;
  message: string;
  remaining_quantity: number;
  evaluation: MultiAgentEvaluationResult;
}

export interface DispensingTransaction {
  id: string;
  prescription_id: string;
  prescription_code?: string;
  prescription_item_id: string;
  medicine_name?: string;
  pharmacy_id: string;
  pharmacy_name?: string;
  requested_quantity: number;
  approved_quantity: number;
  remaining_before: number;
  remaining_after: number;
  status: string;
  rejection_reason?: string;
  transaction_timestamp: string;
  integrity_hash?: string;
}

export interface ReviewCase {
  id: string;
  case_number: string;
  risk_event_id: string;
  prescription_id: string;
  prescription_code?: string;
  patient_id: string;
  patient_name?: string;
  status: 'PENDING' | 'UNDER_REVIEW' | 'APPROVED_OVERRIDE' | 'CONFIRMED_FRAUD' | 'DISMISSED';
  risk_score?: number;
  risk_level?: string;
  ai_summary?: string;
  reviewer_notes?: string;
  resolution_timestamp?: string;
  created_at: string;
}

export interface AuditLog {
  id: string;
  event_type: string;
  actor_user_id?: string;
  actor_role?: string;
  target_entity: string;
  target_id?: string;
  details_json?: Record<string, any>;
  prev_hash?: string;
  sha256_hash: string;
  created_at: string;
}

export interface Warning {
  id: string;
  patient_id: string;
  prescription_id?: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface DemoScenario {
  id: string;
  title: string;
  description: string;
  expected_outcome: string;
  prescription_code: string;
  requested_quantity: number;
  pharmacy_target: string;
  risk_level: string;
}
