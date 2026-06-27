"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ProfileResponse } from "@/lib/types";

function ScoreRing({ score }: { score: number }) {
  const color =
    score >= 75 ? "#3b82f6" : score >= 50 ? "#f59e0b" : "#ef4444";
  const label =
    score >= 75 ? "Competitive" : score >= 50 ? "Developing" : "Not Ready Yet";

  return (
    <div className="flex flex-col items-center gap-2">
      <div
        className="w-36 h-36 rounded-full flex items-center justify-center border-8"
        style={{ borderColor: color }}
      >
        <div className="text-center">
          <div className="text-4xl font-bold" style={{ color }}>
            {score}
          </div>
          <div className="text-xs text-gray-500">/100</div>
        </div>
      </div>
      <span className="text-sm font-medium" style={{ color }}>
        {label}
      </span>
    </div>
  );
}

function Bar({ label, value, max }: { label: string; value: number; max: number }) {
  const pct = Math.round((value / max) * 100);
  const color = pct >= 70 ? "bg-blue-500" : pct >= 45 ? "bg-amber-500" : "bg-red-500";
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-gray-400">{label}</span>
        <span className="text-gray-500">
          {value}/{max}
        </span>
      </div>
      <div className="h-2 bg-white/5 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<ProfileResponse | null>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem("pathforge_profile");
    if (!stored) {
      router.push("/onboarding");
      return;
    }
    setData(JSON.parse(stored));
  }, [router]);

  if (!data) return null;

  const { profile, onboarding } = data;

  return (
    <div className="min-h-screen px-6 py-12 max-w-3xl mx-auto">
      {/* Header */}
      <div className="mb-10">
        <div className="text-sm text-gray-500 mb-1">PathForge Assessment</div>
        <h1 className="text-3xl font-bold">
          {profile.name || "Your"} Honest Career Profile
        </h1>
        <p className="text-gray-500 text-sm mt-2">
          Target: {onboarding.target} · Visa: {onboarding.visa_status} ·{" "}
          {onboarding.hours_per_week}h/week available
        </p>
      </div>

      {/* Score + Breakdown */}
      <div className="bg-white/5 border border-white/10 rounded-xl p-6 mb-6 flex flex-col sm:flex-row gap-8 items-start">
        <ScoreRing score={profile.employability_score} />
        <div className="flex-1 space-y-3 w-full">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
            Score Breakdown
          </h2>
          <Bar label="Skills Breadth & Relevance" value={profile.breakdown.skills_breadth} max={25} />
          <Bar label="Experience Quality & Impact" value={profile.breakdown.experience_quality} max={25} />
          <Bar label="Project Strength" value={profile.breakdown.project_strength} max={20} />
          <Bar label="Education" value={profile.breakdown.education} max={15} />
          <Bar label="Market Alignment" value={profile.breakdown.market_alignment} max={15} />
        </div>
      </div>

      {/* Honest Assessment */}
      <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-5 mb-6">
        <h2 className="text-sm font-semibold text-amber-400 uppercase tracking-wider mb-3">
          Honest Assessment
        </h2>
        <p className="text-gray-300 text-sm leading-relaxed">{profile.honest_assessment}</p>
      </div>

      {/* Gaps */}
      <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-5 mb-6">
        <h2 className="text-sm font-semibold text-red-400 uppercase tracking-wider mb-3">
          What Is Holding You Back
        </h2>
        <ul className="space-y-2">
          {profile.top_gaps.map((gap, i) => (
            <li key={i} className="flex gap-3 text-sm text-gray-300">
              <span className="text-red-400 font-bold flex-shrink-0">{i + 1}.</span>
              {gap}
            </li>
          ))}
        </ul>
      </div>

      {/* Immediate Actions */}
      <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-5 mb-6">
        <h2 className="text-sm font-semibold text-blue-400 uppercase tracking-wider mb-3">
          Do These This Week — In This Order
        </h2>
        <ul className="space-y-3">
          {profile.immediate_actions.map((action, i) => (
            <li key={i} className="flex gap-3 text-sm text-gray-300">
              <span className="bg-blue-500 text-white text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                {i + 1}
              </span>
              {action}
            </li>
          ))}
        </ul>
      </div>

      {/* Skills */}
      <div className="bg-white/5 border border-white/10 rounded-xl p-5 mb-6">
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
          Skills Detected
        </h2>
        <div className="flex flex-wrap gap-2">
          {profile.skills.map((skill) => (
            <span
              key={skill}
              className="bg-white/5 border border-white/10 text-gray-300 text-xs px-3 py-1 rounded-full"
            >
              {skill}
            </span>
          ))}
        </div>
      </div>

      {/* Experience */}
      {profile.experience.length > 0 && (
        <div className="bg-white/5 border border-white/10 rounded-xl p-5 mb-6">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
            Experience
          </h2>
          <div className="space-y-4">
            {profile.experience.map((exp, i) => (
              <div key={i} className="border-l-2 border-white/10 pl-4">
                <div className="font-medium text-sm">{exp.role}</div>
                <div className="text-gray-500 text-xs">{exp.company} · {exp.duration}</div>
                <div className="text-gray-400 text-xs mt-1">{exp.description}</div>
                {exp.impact && (
                  <div className="text-blue-400 text-xs mt-1">Impact: {exp.impact}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Projects */}
      {profile.projects.length > 0 && (
        <div className="bg-white/5 border border-white/10 rounded-xl p-5 mb-6">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
            Projects
          </h2>
          <div className="space-y-4">
            {profile.projects.map((proj, i) => (
              <div key={i} className="border-l-2 border-white/10 pl-4">
                <div className="font-medium text-sm">{proj.name}</div>
                <div className="text-gray-400 text-xs mt-1">{proj.description}</div>
                <div className="flex flex-wrap gap-1 mt-2">
                  {proj.tech_stack.map((t) => (
                    <span
                      key={t}
                      className="bg-blue-500/10 text-blue-400 text-xs px-2 py-0.5 rounded"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* CTA */}
      <div className="text-center pt-4 pb-8">
        <p className="text-gray-500 text-sm mb-4">
          This is your starting point. What you do with it determines the outcome.
        </p>
        <button
          onClick={() => router.push("/onboarding")}
          className="text-blue-400 text-sm hover:text-blue-300 underline"
        >
          Re-run assessment with updated resume
        </button>
      </div>
    </div>
  );
}
