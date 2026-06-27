import { OnboardingData, ProfileResponse, ExtractedProfile, JobMatchResponse } from "./types";

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
