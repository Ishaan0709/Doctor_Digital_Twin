export interface Patient {
  name: string;
  age: number;
  gender: string;
  height_cm: number;
  weight_kg: number;
  symptoms: string;
  symptom_duration: string;
  medical_history: string;
  family_history: string;
  lifestyle: string;
  current_medications: string;
  bp: string;
  ldl: number;
  hba1c: number;
  optional_notes: string;
  profile_id?: string | null;
}

export interface Source {
  type: string;
  id?: string;
  text?: string;
  diagnosis?: string;
  decision?: string;
  outcome?: string;
  score?: number | null;
}

export interface GenericResult {
  consultation_summary: string;
  possible_concerns: string[];
  suggested_next_steps: string[];
  risk_notes: string[];
  clarifying_questions?: string[];
  disclaimer?: string;
  sources?: Source[];
}

export interface CaseMatch {
  case_id?: string;
  symptoms?: string;
  risk_factors?: string;
  tests?: string;
  diagnosis?: string;
  decision?: string;
  outcome?: string;
  match_score?: number;
  final_match_score?: number;
  base_match_score?: number;
  rerank_bonus?: number;
}

export interface TwinResult {
  assessment: string;
  unique_factors: string[];
  historical_patterns: CaseMatch[];
  recommended_tests: string[];
  immediate_actions: string[];
  follow_up_plan: string[];
  confidence_score: number;
  confidence_breakdown?: {
    base?: number;
    retrieval_component?: number;
    graph_component?: number;
    raw_score?: number;
    final_score?: number;
  };
  graph_evidence?: { links?: Array<Record<string, unknown>>; evidence_summary?: string[] };
  sources?: Source[];
  clarifying_questions?: string[];
  disclaimer?: string;
  timeline_context?: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

export type DoctorStatus = "approved" | "edited_approved" | "rejected" | null;

export const demoPatient: Patient = {
  name: "Aarav Mehta",
  age: 52,
  gender: "Male",
  height_cm: 170,
  weight_kg: 78,
  symptoms: "Chest pain / pressure on exertion. Exertional chest pain radiating to left arm, improves with rest.",
  symptom_duration: "2 weeks",
  medical_history: "Type 2 diabetes for 9 years, hypertension for 6 years.\nRisk factors selected: Diabetes, Hypertension, Smoking, Family history of early CAD, High cholesterol",
  family_history: "Father had MI at 54.",
  lifestyle: "Sedentary job, smoker 8 cigarettes/day, low exercise.",
  current_medications: "Metformin, Amlodipine, statin irregularly.",
  bp: "154/96",
  ldl: 186,
  hba1c: 8.4,
  optional_notes: "Pain worse after heavy meals; anxious about heart attack.",
  profile_id: null,
};

export const analysisDefaults: Patient = {
  name: "",
  age: 45,
  gender: "Male",
  height_cm: 170,
  weight_kg: 75,
  symptoms: "Exertional chest discomfort, fatigue",
  symptom_duration: "2 weeks",
  medical_history: "Type 2 diabetes for 8 years",
  family_history: "Father had CAD at 52",
  lifestyle: "Sedentary, moderate stress, occasional smoking",
  current_medications: "Metformin, statin irregularly",
  bp: "130/85",
  ldl: 140,
  hba1c: 6.8,
  optional_notes: "",
  profile_id: null,
};
