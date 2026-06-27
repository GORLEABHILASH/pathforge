"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  ProfileResponse,
  SkillRoadmapResponse,
  SkillRoadmapItem,
  SkillDemand,
  LearningStep,
  SkillProgress,
} from "@/lib/types";
import { getSkillRoadmap, saveProgress, getProgress } from "@/lib/api";

const TREND_CONFIG = {
  exploding: { label: "Exploding", color: "text-green-400", bg: "bg-green-500/10 border-green-500/30" },
  growing: { label: "Growing", color: "text-blue-400", bg: "bg-blue-500/10 border-blue-500/30" },
  stable: { label: "Stable", color: "text-gray-400", bg: "bg-white/5 border-white/10" },
  declining: { label: "Declining", color: "text-red-400", bg: "bg-red-500/10 border-red-500/30" },
};

function SkillDemandCard({ skill }: { skill: SkillDemand }) {
  const trend = TREND_CONFIG[skill.trend];
  const sign = skill.trend_pct >= 0 ? "+" : "";
  return (
    <div className="bg-white/5 border border-white/10 rounded-xl p-4 flex items-center justify-between gap-4">
      <div className="flex-1 min-w-0">
        <div className="font-semibold text-sm">{skill.skill}</div>
        <div className="text-gray-500 text-xs mt-0.5">
          ~{skill.job_count_estimate.toLocaleString()} jobs · +{skill.hire_probability_boost}% hire boost
        </div>
      </div>
      <div className="flex items-center gap-3 flex-shrink-0">
        <div className="text-right">
          <div className="text-lg font-bold text-blue-400">{skill.demand_score}</div>
          <div className="text-gray-600 text-xs">demand</div>
        </div>
        <span className={`text-xs px-2 py-0.5 rounded-full border ${trend.bg} ${trend.color}`}>
          {sign}{skill.trend_pct}% · {trend.label}
        </span>
      </div>
    </div>
  );
}

function StepRow({
  step,
  done,
  onToggle,
}: {
  step: LearningStep;
  done: boolean;
  onToggle: (order: number) => void;
}) {
  return (
    <div
      className={`flex gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
        done
          ? "bg-blue-500/10 border-blue-500/20"
          : "bg-white/3 border-white/5 hover:border-white/15"
      }`}
      onClick={() => onToggle(step.order)}
    >
      <div
        className={`w-5 h-5 rounded-full border flex items-center justify-center flex-shrink-0 mt-0.5 ${
          done ? "bg-blue-500 border-blue-500" : "border-gray-600"
        }`}
      >
        {done && <span className="text-white text-xs">✓</span>}
      </div>
      <div className="flex-1 min-w-0">
        <div className={`text-sm font-medium ${done ? "line-through text-gray-500" : ""}`}>
          {step.what}
        </div>
        <div className="text-gray-500 text-xs mt-0.5">{step.how}</div>
        <div className="flex gap-4 mt-1.5">
          <span className="text-gray-600 text-xs">⏱ {step.time_estimate}</span>
          <span className="text-blue-400/70 text-xs">→ {step.deliverable}</span>
        </div>
      </div>
    </div>
  );
}

function RoadmapCard({
  item,
  progress,
  onStepToggle,
}: {
  item: SkillRoadmapItem;
  progress: SkillProgress | undefined;
  onStepToggle: (skill: string, order: number) => void;
}) {
  const completedSteps = progress?.completed_steps ?? [];
  const total = item.steps.length;
  const done = completedSteps.length;
  const pct = total > 0 ? Math.round((done / total) * 100) : 0;

  return (
    <div className="bg-white/5 border border-white/10 rounded-xl p-5">
      <div className="flex items-start justify-between gap-3 mb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="bg-blue-500/20 text-blue-400 text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center">
              {item.priority}
            </span>
            <h3 className="font-semibold">{item.skill}</h3>
            <span className="text-xs text-gray-500">
              {item.current_level} → {item.target_level}
            </span>
          </div>
          <p className="text-gray-400 text-xs mt-1.5 leading-relaxed">{item.why_it_matters}</p>
        </div>
        <div className="text-right flex-shrink-0">
          <div className="text-green-400 font-bold text-sm">+{item.hire_probability_boost}%</div>
          <div className="text-gray-600 text-xs">hire boost</div>
        </div>
      </div>

      {/* Progress bar */}
      <div className="mb-4">
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>{done}/{total} steps complete</span>
          <span>{pct}%</span>
        </div>
        <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-500 rounded-full transition-all duration-300"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      <div className="space-y-2">
        {item.steps.map((step) => (
          <StepRow
            key={step.order}
            step={step}
            done={completedSteps.includes(step.order)}
            onToggle={(order) => onStepToggle(item.skill, order)}
          />
        ))}
      </div>
    </div>
  );
}

export default function SkillsPage() {
  const router = useRouter();
  const [profileData, setProfileData] = useState<ProfileResponse | null>(null);
  const [roadmap, setRoadmap] = useState<SkillRoadmapResponse | null>(null);
  const [progress, setProgress] = useState<SkillProgress[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"market" | "roadmap">("roadmap");

  useEffect(() => {
    const stored = sessionStorage.getItem("pathforge_profile");
    if (!stored) {
      router.push("/onboarding");
      return;
    }
    const data: ProfileResponse = JSON.parse(stored);
    setProfileData(data);

    // Load cached roadmap
    const cached = sessionStorage.getItem("pathforge_roadmap");
    if (cached) setRoadmap(JSON.parse(cached));

    // Load progress from localStorage (works without Supabase)
    const localProgress = localStorage.getItem(`pathforge_progress_${data.onboarding.email}`);
    if (localProgress) setProgress(JSON.parse(localProgress));

    // Load progress from Supabase if available
    getProgress(data.onboarding.email).then((remote) => {
      if (remote.length > 0) {
        setProgress(remote);
        localStorage.setItem(
          `pathforge_progress_${data.onboarding.email}`,
          JSON.stringify(remote)
        );
      }
    });
  }, [router]);

  const fetchRoadmap = useCallback(async () => {
    if (!profileData) return;
    setLoading(true);
    setError("");
    try {
      const result = await getSkillRoadmap(profileData.profile, profileData.onboarding);
      sessionStorage.setItem("pathforge_roadmap", JSON.stringify(result));
      setRoadmap(result);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to generate roadmap");
    } finally {
      setLoading(false);
    }
  }, [profileData]);

  useEffect(() => {
    if (profileData && !sessionStorage.getItem("pathforge_roadmap")) {
      fetchRoadmap();
    }
  }, [profileData, fetchRoadmap]);

  const handleStepToggle = useCallback(
    async (skill: string, order: number) => {
      if (!profileData) return;
      const email = profileData.onboarding.email;

      setProgress((prev) => {
        const existing = prev.find((p) => p.skill === skill);
        let updated: SkillProgress[];
        if (existing) {
          const steps = existing.completed_steps.includes(order)
            ? existing.completed_steps.filter((s) => s !== order)
            : [...existing.completed_steps, order];
          updated = prev.map((p) => (p.skill === skill ? { ...p, completed_steps: steps } : p));
        } else {
          updated = [...prev, { skill, completed_steps: [order] }];
        }
        // Save to localStorage immediately
        localStorage.setItem(`pathforge_progress_${email}`, JSON.stringify(updated));
        // Save to Supabase in background
        const entry = updated.find((p) => p.skill === skill);
        if (entry) saveProgress(email, skill, entry.completed_steps);
        return updated;
      });
    },
    [profileData]
  );

  if (!profileData) return null;

  const totalBoost = roadmap?.your_gaps.reduce((sum, g) => sum + g.hire_probability_boost, 0) ?? 0;

  return (
    <div className="min-h-screen px-6 py-12 max-w-3xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="text-sm text-gray-500 mb-1">PathForge · Skill Intelligence</div>
        <h1 className="text-3xl font-bold">Your Learning Roadmap</h1>
        <p className="text-gray-500 text-sm mt-2">
          What to learn, in what order, and exactly how to learn it.
        </p>
      </div>

      {/* Probability banner */}
      {roadmap && (
        <div className="bg-white/5 border border-white/10 rounded-xl p-5 mb-6 flex flex-col sm:flex-row gap-4 items-center">
          <div className="text-center">
            <div className="text-3xl font-bold text-red-400">{roadmap.current_hire_probability}%</div>
            <div className="text-xs text-gray-500 mt-0.5">current hire probability</div>
          </div>
          <div className="flex-1 flex items-center gap-2">
            <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-red-500 to-blue-500 rounded-full"
                style={{ width: `${roadmap.projected_hire_probability}%` }}
              />
            </div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-400">{roadmap.projected_hire_probability}%</div>
            <div className="text-xs text-gray-500 mt-0.5">after roadmap · ~{roadmap.total_weeks_to_ready} weeks</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {(["roadmap", "market"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors ${
              activeTab === tab
                ? "border-blue-500 bg-blue-500/10 text-blue-400"
                : "border-white/10 text-gray-500 hover:border-white/20"
            }`}
          >
            {tab === "roadmap" ? "Your Roadmap" : "Market Demand"}
          </button>
        ))}
      </div>

      {/* Loading */}
      {loading && (
        <div className="bg-white/5 border border-white/10 rounded-xl p-12 text-center">
          <p className="text-gray-500 text-sm">Analyzing the job market for your profile...</p>
          <p className="text-gray-600 text-xs mt-1">This takes about 20 seconds.</p>
        </div>
      )}

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 mb-4">
          <p className="text-red-400 text-sm">{error}</p>
          <button
            onClick={fetchRoadmap}
            className="text-red-300 text-xs underline mt-2"
          >
            Try again
          </button>
        </div>
      )}

      {/* Roadmap tab */}
      {!loading && roadmap && activeTab === "roadmap" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-sm">
              Complete these in order. Each one directly increases your hire probability.
            </p>
            <span className="text-blue-400 text-sm font-semibold">+{totalBoost}% total boost</span>
          </div>
          {roadmap.your_gaps.map((item) => (
            <RoadmapCard
              key={item.skill}
              item={item}
              progress={progress.find((p) => p.skill === item.skill)}
              onStepToggle={handleStepToggle}
            />
          ))}
          <button
            onClick={fetchRoadmap}
            className="text-gray-600 text-xs hover:text-gray-400 w-full text-center mt-2"
          >
            ↻ Regenerate roadmap
          </button>
        </div>
      )}

      {/* Market demand tab */}
      {!loading && roadmap && activeTab === "market" && (
        <div className="space-y-3">
          <p className="text-gray-400 text-sm mb-4">
            Current skill demand for your target role. Skills you already have are included so you can see the full market picture.
          </p>
          {roadmap.top_market_skills.map((skill) => (
            <SkillDemandCard key={skill.skill} skill={skill} />
          ))}
        </div>
      )}

      {/* CTA back to dashboard */}
      <div className="text-center pt-8 pb-4">
        <button
          onClick={() => router.push("/dashboard")}
          className="text-gray-600 text-sm hover:text-gray-400"
        >
          ← Back to Dashboard
        </button>
      </div>
    </div>
  );
}
