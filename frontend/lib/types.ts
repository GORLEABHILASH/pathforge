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
