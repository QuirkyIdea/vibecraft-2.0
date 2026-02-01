import type { Metadata } from "next";
import "./globals.css";
import { StatsProvider } from "@/context/StatsContext";
import { AuthProvider } from "@/context/AuthContext";
import { ProjectProvider } from "@/context/ProjectContext";

export const metadata: Metadata = {
  title: "Inventix AI - Evidence-Locked Research & Patent Intelligence",
  description: "ANTIGRAVITY: A constrained intelligence system for research and patent analysis. Evidence-grounded. Probabilistic. Auditable.",
  keywords: ["patent intelligence", "research analysis", "prior art", "novelty detection", "AI"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <div className="gradient-bg" />
        <AuthProvider>
          <ProjectProvider>
            <StatsProvider>
              {children}
            </StatsProvider>
          </ProjectProvider>
        </AuthProvider>
      </body>
    </html>
  );
}

