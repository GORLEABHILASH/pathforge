"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { OnboardingData, VisaStatus, CompanyTarget } from "@/lib/types";
import { assessProfile, extractPdfText } from "@/lib/api";

const VISA_OPTIONS: VisaStatus[] = [
  "F-1 Student",
  "OPT",
  "STEM OPT",
  "H-1B",
  "Green Card",
  "US Citizen",
  "Other",
];

const TARGET_OPTIONS: { value: CompanyTarget; label: string; desc: string }[] = [
  { value: "FAANG / Top Tier", label: "FAANG / Top Tier", desc: "Google, Meta, Amazon, Apple, Microsoft, OpenAI" },
  { value: "High Growth Tech", label: "High Growth Tech", desc: "Stripe, Airbnb, Figma, Notion, Vercel" },
  { value: "Any Tech Company", label: "Any Tech Company", desc: "Any reputable tech company" },
  { value: "Just Get Employed", label: "Just Get Employed", desc: "Any organization — I need a job" },
  { value: "Specific Companies", label: "Specific Companies", desc: "I have specific targets in mind" },
];

const STEPS = ["Start", "Resume", "Context", "Target", "Assess"];

const empty: OnboardingData = {
  email: "",
  resume_text: "",
  visa_status: "F-1 Student",
  target: "Any Tech Company",
  specific_companies: [],
  hours_per_week: 10,
  goal: "",
};

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [data, setData] = useState<OnboardingData>(empty);
  const [resumeMode, setResumeMode] = useState<"paste" | "upload">("paste");
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [specificInput, setSpecificInput] = useState("");

  const update = (patch: Partial<OnboardingData>) =>
    setData((prev) => ({ ...prev, ...patch }));

  const next = () => setStep((s) => s + 1);
  const back = () => setStep((s) => s - 1);

  async function handlePdfUpload(file: File) {
    setUploading(true);
    setError("");
    try {
      const text = await extractPdfText(file);
      update({ resume_text: text });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "PDF upload failed");
    } finally {
      setUploading(false);
    }
  }

  async function handleAssess() {
    setLoading(true);
    setError("");
    try {
      const result = await assessProfile(data);
      sessionStorage.setItem("pathforge_profile", JSON.stringify(result));
      router.push("/dashboard");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Assessment failed. Please try again.");
      setLoading(false);
    }
  }

  const canProceed = [
    data.email.includes("@"),
    data.resume_text.trim().length > 100,
    data.visa_status && data.hours_per_week > 0 && data.goal.trim().length > 10,
    data.target !== undefined,
    true,
  ][step];

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 py-12">
      {/* Progress */}
      <div className="w-full max-w-xl mb-10">
        <div className="flex items-center gap-2">
          {STEPS.map((s, i) => (
            <div key={s} className="flex items-center gap-2 flex-1">
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                  i < step
                    ? "bg-blue-500 text-white"
                    : i === step
                    ? "bg-blue-500/20 border border-blue-500 text-blue-400"
                    : "bg-white/5 text-gray-600"
                }`}
              >
                {i < step ? "✓" : i + 1}
              </div>
              <span className={`text-xs hidden sm:block ${i === step ? "text-blue-400" : "text-gray-600"}`}>
                {s}
              </span>
              {i < STEPS.length - 1 && (
                <div className={`flex-1 h-px ${i < step ? "bg-blue-500" : "bg-white/10"}`} />
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="w-full max-w-xl">
        {/* Step 0 — Email */}
        {step === 0 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Let&apos;s start with your email</h2>
              <p className="text-gray-400 text-sm">
                This is where we&apos;ll send your assessment results. No spam, ever.
              </p>
            </div>
            <input
              type="email"
              placeholder="you@email.com"
              value={data.email}
              onChange={(e) => update({ email: e.target.value })}
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-blue-500"
            />
          </div>
        )}

        {/* Step 1 — Resume */}
        {step === 1 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Upload your resume</h2>
              <p className="text-gray-400 text-sm">
                The AI will extract your skills, experience, and projects. Be honest — it gives honest feedback.
              </p>
            </div>
            <div className="flex gap-3">
              {(["paste", "upload"] as const).map((m) => (
                <button
                  key={m}
                  onClick={() => setResumeMode(m)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors ${
                    resumeMode === m
                      ? "border-blue-500 bg-blue-500/10 text-blue-400"
                      : "border-white/10 text-gray-500 hover:border-white/20"
                  }`}
                >
                  {m === "paste" ? "Paste Text" : "Upload PDF"}
                </button>
              ))}
            </div>

            {resumeMode === "paste" ? (
              <textarea
                placeholder="Paste your full resume text here..."
                value={data.resume_text}
                onChange={(e) => update({ resume_text: e.target.value })}
                rows={12}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-blue-500 resize-none text-sm"
              />
            ) : (
              <div className="border-2 border-dashed border-white/10 rounded-lg p-8 text-center">
                <input
                  type="file"
                  accept=".pdf"
                  id="pdf-upload"
                  className="hidden"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) handlePdfUpload(file);
                  }}
                />
                <label htmlFor="pdf-upload" className="cursor-pointer">
                  {uploading ? (
                    <p className="text-blue-400">Extracting text from PDF...</p>
                  ) : data.resume_text ? (
                    <p className="text-green-400">✓ Resume extracted successfully</p>
                  ) : (
                    <>
                      <p className="text-gray-400 mb-2">Click to upload PDF</p>
                      <p className="text-gray-600 text-xs">Max 5MB</p>
                    </>
                  )}
                </label>
              </div>
            )}
          </div>
        )}

        {/* Step 2 — Context */}
        {step === 2 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Tell us your situation</h2>
              <p className="text-gray-400 text-sm">
                This determines what&apos;s realistically possible and the honest path to get there.
              </p>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">Visa Status</label>
              <div className="grid grid-cols-2 gap-2">
                {VISA_OPTIONS.map((v) => (
                  <button
                    key={v}
                    onClick={() => update({ visa_status: v })}
                    className={`px-3 py-2 rounded-lg text-sm border transition-colors text-left ${
                      data.visa_status === v
                        ? "border-blue-500 bg-blue-500/10 text-blue-400"
                        : "border-white/10 text-gray-400 hover:border-white/20"
                    }`}
                  >
                    {v}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Hours per week you can commit to job searching / upskilling
              </label>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  min={2}
                  max={40}
                  value={data.hours_per_week}
                  onChange={(e) => update({ hours_per_week: Number(e.target.value) })}
                  className="flex-1 accent-blue-500"
                />
                <span className="text-blue-400 font-bold w-16 text-right">
                  {data.hours_per_week}h/wk
                </span>
              </div>
              {data.hours_per_week < 5 && (
                <p className="text-amber-500 text-xs mt-2">
                  Under 5 hours/week significantly limits what we can help you achieve.
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">
                What is your goal right now? (Be specific)
              </label>
              <textarea
                placeholder="e.g. I want a software engineering role at a startup that sponsors OPT. I have 3 months before my CPT expires."
                value={data.goal}
                onChange={(e) => update({ goal: e.target.value })}
                rows={3}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-600 focus:outline-none focus:border-blue-500 resize-none text-sm"
              />
            </div>
          </div>
        )}

        {/* Step 3 — Target */}
        {step === 3 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">What are you targeting?</h2>
              <p className="text-gray-400 text-sm">
                Be honest. The platform gives different guidance for different targets.
                Choosing FAANG when you are not ready wastes your time.
              </p>
            </div>

            <div className="space-y-2">
              {TARGET_OPTIONS.map((t) => (
                <button
                  key={t.value}
                  onClick={() => update({ target: t.value })}
                  className={`w-full px-4 py-3 rounded-lg border text-left transition-colors ${
                    data.target === t.value
                      ? "border-blue-500 bg-blue-500/10"
                      : "border-white/10 hover:border-white/20"
                  }`}
                >
                  <div className="font-medium text-sm">{t.label}</div>
                  <div className="text-xs text-gray-500 mt-0.5">{t.desc}</div>
                </button>
              ))}
            </div>

            {data.target === "Specific Companies" && (
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  Which companies? (press Enter to add)
                </label>
                <div className="flex gap-2 mb-2">
                  <input
                    value={specificInput}
                    onChange={(e) => setSpecificInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && specificInput.trim()) {
                        update({ specific_companies: [...data.specific_companies, specificInput.trim()] });
                        setSpecificInput("");
                      }
                    }}
                    placeholder="e.g. Stripe"
                    className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div className="flex flex-wrap gap-2">
                  {data.specific_companies.map((c) => (
                    <span
                      key={c}
                      className="bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs px-2 py-1 rounded-full flex items-center gap-1"
                    >
                      {c}
                      <button
                        onClick={() =>
                          update({ specific_companies: data.specific_companies.filter((x) => x !== c) })
                        }
                        className="ml-1 text-blue-300 hover:text-white"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Step 4 — Assess */}
        {step === 4 && (
          <div className="space-y-6 text-center">
            <div>
              <h2 className="text-2xl font-bold mb-2">Ready for your honest assessment</h2>
              <p className="text-gray-400 text-sm max-w-md mx-auto">
                The AI will analyze your resume and give you a brutally honest employability score,
                your real gaps, and exactly what to do next.
              </p>
            </div>

            <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-4 text-sm text-amber-400 text-left">
              <strong>Before you proceed:</strong> This assessment will not be gentle.
              If your resume is weak, it will say so. If your target is unrealistic,
              it will say so. That honesty is what makes it useful.
            </div>

            <div className="space-y-2 text-sm text-gray-500 text-left">
              <div className="flex gap-2"><span className="text-blue-400">→</span> Email: {data.email}</div>
              <div className="flex gap-2"><span className="text-blue-400">→</span> Visa: {data.visa_status}</div>
              <div className="flex gap-2"><span className="text-blue-400">→</span> Target: {data.target}</div>
              <div className="flex gap-2"><span className="text-blue-400">→</span> Commitment: {data.hours_per_week}h/week</div>
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-lg p-3 text-sm">
                {error}
              </div>
            )}

            <button
              onClick={handleAssess}
              disabled={loading}
              className="w-full bg-blue-500 hover:bg-blue-400 disabled:bg-blue-500/30 disabled:cursor-not-allowed text-white font-semibold px-6 py-4 rounded-lg transition-colors"
            >
              {loading ? "Analyzing your profile..." : "Run My Honest Assessment →"}
            </button>

            {loading && (
              <p className="text-gray-500 text-xs">
                This takes 15-30 seconds. The AI is reading your full resume carefully.
              </p>
            )}
          </div>
        )}

        {/* Navigation */}
        {step < 4 && (
          <div className="flex gap-3 mt-8">
            {step > 0 && (
              <button
                onClick={back}
                className="px-6 py-3 rounded-lg border border-white/10 text-gray-400 hover:border-white/20 transition-colors"
              >
                Back
              </button>
            )}
            <button
              onClick={next}
              disabled={!canProceed}
              className="flex-1 bg-blue-500 hover:bg-blue-400 disabled:bg-white/5 disabled:text-gray-600 disabled:cursor-not-allowed text-white font-semibold px-6 py-3 rounded-lg transition-colors"
            >
              Continue →
            </button>
          </div>
        )}

        {step === 4 && (
          <button onClick={back} className="mt-4 text-sm text-gray-600 hover:text-gray-400 w-full text-center">
            ← Go back and edit
          </button>
        )}
      </div>
    </div>
  );
}
