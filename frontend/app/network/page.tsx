"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ProfileResponse, OutreachMessage, NetworkAnalysisResponse, JobMatchResponse } from "@/lib/types";
import { analyzeNetwork } from "@/lib/api";

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={() => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }}
      className="text-xs px-3 py-1.5 rounded-lg border border-white/10 text-gray-400 hover:border-blue-500/50 hover:text-blue-400 transition-colors"
    >
      {copied ? "Copied ✓" : "Copy"}
    </button>
  );
}

function OutreachCard({ msg }: { msg: OutreachMessage }) {
  const [expanded, setExpanded] = useState(false);
  const scoreColor =
    msg.relevance_score >= 75 ? "#3b82f6" : msg.relevance_score >= 50 ? "#f59e0b" : "#6b7280";

  return (
    <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
      {/* Header */}
      <div
        className="p-5 flex items-start justify-between gap-4 cursor-pointer hover:bg-white/3 transition-colors"
        onClick={() => setExpanded((e) => !e)}
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-semibold text-sm">{msg.connection.full_name}</span>
            {msg.company_is_hiring && (
              <span className="text-xs bg-green-500/10 border border-green-500/30 text-green-400 px-2 py-0.5 rounded-full">
                Actively Hiring
              </span>
            )}
          </div>
          <div className="text-gray-400 text-xs mt-0.5">
            {msg.connection.position} · {msg.connection.company}
          </div>
          <p className="text-gray-500 text-xs mt-1.5 leading-relaxed">{msg.why_relevant}</p>
        </div>
        <div className="text-right flex-shrink-0">
          <div className="text-xl font-bold" style={{ color: scoreColor }}>
            {msg.relevance_score}
          </div>
          <div className="text-gray-600 text-xs">relevance</div>
        </div>
      </div>

      {/* Expanded message */}
      {expanded && (
        <div className="border-t border-white/10 p-5 space-y-4">
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs text-gray-500 uppercase tracking-wider">Subject</span>
              <CopyButton text={msg.subject} />
            </div>
            <p className="text-sm text-gray-300 bg-white/3 rounded-lg px-3 py-2">{msg.subject}</p>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs text-gray-500 uppercase tracking-wider">Message</span>
              <CopyButton text={msg.message} />
            </div>
            <pre className="text-sm text-gray-300 bg-white/3 rounded-lg px-4 py-3 whitespace-pre-wrap font-sans leading-relaxed">
              {msg.message}
            </pre>
          </div>

          {msg.connection.linkedin_url && (
            <a
              href={msg.connection.linkedin_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block text-xs text-blue-400 hover:text-blue-300 underline"
            >
              Open LinkedIn profile →
            </a>
          )}
        </div>
      )}
    </div>
  );
}

export default function NetworkPage() {
  const router = useRouter();
  const [profileData, setProfileData] = useState<ProfileResponse | null>(null);
  const [result, setResult] = useState<NetworkAnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem("pathforge_profile");
    if (!stored) { router.push("/onboarding"); return; }
    setProfileData(JSON.parse(stored));

    const cached = sessionStorage.getItem("pathforge_network");
    if (cached) setResult(JSON.parse(cached));
  }, [router]);

  async function handleFile(file: File) {
    if (!profileData) return;
    if (!file.name.toLowerCase().endsWith(".csv")) {
      setError("Please upload a CSV file — LinkedIn exports as .csv");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const jobsCache = sessionStorage.getItem("pathforge_jobs");
    const jobCompanies: string[] = jobsCache
      ? (JSON.parse(jobsCache) as JobMatchResponse).jobs.map((j) => j.company)
      : [];

    try {
      const { profile, onboarding } = profileData;
      const data = await analyzeNetwork(file, {
        candidate_name: profile.name,
        candidate_skills: profile.skills,
        candidate_email: onboarding.email,
        target: onboarding.target,
        goal: onboarding.goal,
        visa_status: onboarding.visa_status,
        specific_companies: onboarding.specific_companies,
        matched_job_companies: jobCompanies,
      });
      sessionStorage.setItem("pathforge_network", JSON.stringify(data));
      setResult(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Network analysis failed");
    } finally {
      setLoading(false);
    }
  }

  if (!profileData) return null;

  return (
    <div className="min-h-screen px-6 py-12 max-w-3xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="text-sm text-gray-500 mb-1">PathForge · Warm Introductions</div>
        <h1 className="text-3xl font-bold">Your Network</h1>
        <p className="text-gray-500 text-sm mt-2">
          70% of jobs are filled through referrals. Upload your LinkedIn connections and we&apos;ll
          generate personalized outreach messages for every relevant contact.
        </p>
      </div>

      {/* Stats banner if results exist */}
      {result && (
        <div className="grid grid-cols-3 gap-4 mb-8">
          {[
            { label: "Total connections", value: result.total_connections },
            { label: "Relevant matches", value: result.matched_connections },
            { label: "Outreach ready", value: result.outreach_messages.length },
          ].map((s) => (
            <div key={s.label} className="bg-white/5 border border-white/10 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-blue-400">{s.value}</div>
              <div className="text-gray-500 text-xs mt-0.5">{s.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Upload zone — always visible if no results yet */}
      {!result && (
        <div className="mb-8">
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 mb-5 text-sm text-amber-400">
            <strong>How to export your LinkedIn connections:</strong>
            <ol className="mt-2 space-y-1 text-xs list-decimal list-inside text-amber-300">
              <li>Go to linkedin.com → Me → Settings &amp; Privacy</li>
              <li>Data privacy → Get a copy of your data</li>
              <li>Select &quot;Connections&quot; only → Request archive</li>
              <li>Download and upload the Connections.csv here</li>
            </ol>
          </div>

          <div
            className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors cursor-pointer ${
              dragOver
                ? "border-blue-500 bg-blue-500/5"
                : "border-white/10 hover:border-white/20"
            }`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragOver(false);
              const file = e.dataTransfer.files[0];
              if (file) handleFile(file);
            }}
            onClick={() => fileRef.current?.click()}
          >
            <input
              ref={fileRef}
              type="file"
              accept=".csv"
              className="hidden"
              onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
            />
            {loading ? (
              <div>
                <p className="text-blue-400 text-sm font-medium">Analyzing your network...</p>
                <p className="text-gray-600 text-xs mt-1">
                  Reading connections, finding matches, writing outreach messages
                </p>
              </div>
            ) : (
              <div>
                <p className="text-gray-400 text-sm">Drop your Connections.csv here</p>
                <p className="text-gray-600 text-xs mt-1">or click to browse</p>
              </div>
            )}
          </div>

          {error && (
            <div className="mt-4 bg-red-500/10 border border-red-500/20 rounded-xl p-4">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}
        </div>
      )}

      {/* Results */}
      {result && (
        <div>
          {result.outreach_messages.length === 0 ? (
            <div className="bg-white/5 border border-white/10 rounded-xl p-8 text-center mb-6">
              <p className="text-gray-400 text-sm">
                No connections found at relevant companies in your network.
              </p>
              <p className="text-gray-600 text-xs mt-1">
                This means cold applications are your current path — focus on the job matching and
                skill roadmap first to strengthen your profile.
              </p>
            </div>
          ) : (
            <div className="space-y-3 mb-6">
              <p className="text-gray-400 text-sm mb-4">
                Click any card to see the outreach message. Start with the highest-scored connections
                at companies marked &quot;Actively Hiring&quot;.
              </p>
              {result.outreach_messages.map((msg, i) => (
                <OutreachCard key={i} msg={msg} />
              ))}
            </div>
          )}

          {/* Re-upload */}
          <div className="text-center">
            <button
              onClick={() => { setResult(null); sessionStorage.removeItem("pathforge_network"); }}
              className="text-gray-600 text-xs hover:text-gray-400"
            >
              ↻ Upload a different connections file
            </button>
          </div>
        </div>
      )}

      <div className="text-center pt-8 pb-4">
        <Link href="/dashboard" className="text-gray-600 text-sm hover:text-gray-400">
          ← Back to Dashboard
        </Link>
      </div>
    </div>
  );
}
