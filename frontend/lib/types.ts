export type VisaStatus =
  | "F-1 Student"
  | "OPT"
  | "STEM OPT"
  | "H-1B"
  | "Green Card"
  | "US Citizen"
  | "Other";

export type CompanyTarget =
  | "FAANG / Top Tier"
  | "High Growth Tech"
  | "Any Tech Company"
  | "Just Get Employed"
  | "Specific Companies";

export interface OnboardingData {
  email: string;
  resume_text: string;
  visa_status: VisaStatus;
  target: CompanyTarget;
  specific_companies: string[];
  hours_per_week: number;
  goal: string;
}

export interface EmployabilityBreakdown {
  skills_breadth: number;
  experience_quality: number;
  project_strength: number;
  education: number;
  market_alignment: number;
}

export interface Experience {
  company: string;
  role: string;
  duration: string;
  description: string;
  impact?: string;
}

export interface Project {
  name: string;
  description: string;
  tech_stack: string[];
  impact?: string;
  url?: string;
}

export interface Education {
  institution: string;
  degree: string;
  field: string;
  graduation_year?: string;
  gpa?: number;
}

export interface ExtractedProfile {
  name: string;
  skills: string[];
  experience: Experience[];
  projects: Project[];
  education: Education[];
  employability_score: number;
  breakdown: EmployabilityBreakdown;
  honest_assessment: string;
  top_gaps: string[];
  immediate_actions: string[];
}

export interface ProfileResponse {
  profile: ExtractedProfile;
  onboarding: OnboardingData;
  email: string;
}

export type VisaConfidence = "confirmed" | "likely" | "unknown" | "not_required";

export interface MatchedJob {
  job_id: string;
  title: string;
  company: string;
  location: string;
  apply_link: string | null;
  is_remote: boolean;
  match_score: number;
  visa_confidence: VisaConfidence;
  visa_signal: string;
  why_match: string;
  employment_type: string | null;
}

export interface JobMatchResponse {
  jobs: MatchedJob[];
  total_fetched: number;
  total_after_visa_filter: number;
  used_stub: boolean;
}

// Skill demand + roadmap types
export interface SkillDemand {
  skill: string;
  demand_score: number;
  trend: "exploding" | "growing" | "stable" | "declining";
  trend_pct: number;
  job_count_estimate: number;
  hire_probability_boost: number;
}

export interface LearningStep {
  order: number;
  what: string;
  how: string;
  time_estimate: string;
  deliverable: string;
}

export interface SkillRoadmapItem {
  skill: string;
  priority: number;
  current_level: "none" | "beginner" | "intermediate";
  target_level: "working" | "proficient" | "expert";
  why_it_matters: string;
  hire_probability_boost: number;
  steps: LearningStep[];
}

export interface SkillRoadmapResponse {
  top_market_skills: SkillDemand[];
  your_gaps: SkillRoadmapItem[];
  total_weeks_to_ready: number;
  current_hire_probability: number;
  projected_hire_probability: number;
}

// Progress tracking (persisted in Supabase, cached in localStorage)
export interface SkillProgress {
  skill: string;
  completed_steps: number[];
  notes?: string;
}
