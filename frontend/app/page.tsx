import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-6 text-center">
      <div className="max-w-2xl">
        <div className="inline-block bg-blue-500/10 border border-blue-500/30 text-blue-400 text-sm px-3 py-1 rounded-full mb-8">
          Built for international students in tech
        </div>

        <h1 className="text-5xl font-bold tracking-tight mb-6 leading-tight">
          No hardworking engineer
          <br />
          <span className="text-blue-400">should be unemployed.</span>
        </h1>

        <p className="text-lg text-gray-400 mb-4 leading-relaxed">
          PathForge gives you an honest picture of where you stand, tells you
          exactly what to fix, and matches you to companies that need what
          you&apos;ve actually built.
        </p>

        <p className="text-sm text-gray-500 mb-10">
          We will not tell you what you want to hear. We will tell you what you
          need to hear.
        </p>

        <Link
          href="/onboarding"
          className="inline-block bg-blue-500 hover:bg-blue-400 text-white font-semibold px-8 py-4 rounded-lg text-lg transition-colors"
        >
          Get Your Honest Assessment →
        </Link>

        <p className="mt-4 text-xs text-gray-600">
          Free. No credit card. Takes 5 minutes.
        </p>
      </div>

      <div className="mt-24 grid grid-cols-3 gap-12 text-center max-w-2xl">
        {[
          { stat: "72-78%", label: "placement rate for engaged users" },
          { stat: "60 days", label: "average time to hire" },
          { stat: "0", label: "false promises made" },
        ].map((item) => (
          <div key={item.stat}>
            <div className="text-3xl font-bold text-blue-400">{item.stat}</div>
            <div className="text-sm text-gray-500 mt-1">{item.label}</div>
          </div>
        ))}
      </div>
    </main>
  );
}
