import {
  OnboardingData,
  ProfileResponse,
  ExtractedProfile,
  JobMatchResponse,
  SkillRoadmapResponse,
  SkillProgress,
  NetworkAnalysisResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function assessProfile(data: OnboardingData): Promise<ProfileResponse> {
  const res = await fetch(`${API_BASE}/api/profile/assess`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: data.email,
      onboarding: {
        resume_text: data.resume_text,
        visa_status: data.visa_status,
        target: data.target,
        specific_companies: data.specific_companies,
        hours_per_week: data.hours_per_week,
        goal: data.goal,
      },
    }),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Assessment failed");
  }

  return res.json();
}

export async function matchJobs(
  profile: ExtractedProfile,
  onboarding: OnboardingData
): Promise<JobMatchResponse> {
  const res = await fetch(`${API_BASE}/api/jobs/match`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile, onboarding }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Job matching failed");
  }
  return res.json();
}

export async function getSkillRoadmap(
  profile: ExtractedProfile,
  onboarding: OnboardingData
): Promise<SkillRoadmapResponse> {
  const res = await fetch(`${API_BASE}/api/skills/roadmap`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile, onboarding }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Skill roadmap failed");
  }
  return res.json();
}

export async function saveProgress(
  email: string,
  skill: string,
  completed_steps: number[],
  notes?: string
): Promise<void> {
  await fetch(`${API_BASE}/api/skills/progress`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_email: email, skill, completed_steps, notes }),
  });
}

export async function getProgress(email: string): Promise<SkillProgress[]> {
  const res = await fetch(`${API_BASE}/api/skills/progress/${encodeURIComponent(email)}`);
  if (!res.ok) return [];
  const data = await res.json();
  return data.progress || [];
}

export async function extractPdfText(file: File): Promise<string> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/api/profile/extract-from-pdf`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "PDF extraction failed");
  }

  const data = await res.json();
  return data.resume_text;
}

export async function analyzeNetwork(
  file: File,
  context: {
    candidate_name: string;
    candidate_skills: string[];
    candidate_email: string;
    target: string;
    goal: string;
    visa_status: string;
    specific_companies?: string[];
    matched_job_companies?: string[];
  }
): Promise<NetworkAnalysisResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("request_json", JSON.stringify(context));

  const res = await fetch(`${API_BASE}/api/network/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Network analysis failed");
  }
  return res.json();
}
