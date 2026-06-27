import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PathForge — Get Hired",
  description: "No hardworking engineer should be unemployed. PathForge gets you hired.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full bg-[#0a0a0f] text-[#f0f0f5] antialiased">
        {children}
      </body>
    </html>
  );
}
