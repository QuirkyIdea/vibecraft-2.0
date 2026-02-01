"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import IdeaAnalyzer from "@/components/panels/IdeaAnalyzer";
import PatentRiskPanel from "@/components/panels/PatentRiskPanel";
import KnowledgeGraphPanel from "@/components/panels/KnowledgeGraphPanel";
import ResearchPanel from "@/components/panels/ResearchPanel";
import DashboardOverview from "@/components/panels/DashboardOverview";
import ProjectDashboard from "@/components/panels/ProjectDashboard";
import ProjectDetailView from "@/components/panels/ProjectDetailView";
import RoadmapCreator from "@/components/panels/RoadmapCreator";
import PipelineStatus from "@/components/panels/PipelineStatus";
import AntigravityPanel from "@/components/panels/AntigravityPanel";
import { useAuth } from "@/context/AuthContext";
import { useProjects } from "@/context/ProjectContext";
import styles from "./page.module.css";

export type PanelType = "dashboard" | "projects" | "project_detail" | "antigravity" | "idea" | "patent" | "research" | "knowledge" | "roadmap" | "pipeline";

export default function Home() {
  const [activePanel, setActivePanel] = useState<PanelType>("dashboard");
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const { selectProject, selectedProject, clearSelectedProject } = useProjects();

  // When a project is selected, load it
  useEffect(() => {
    if (selectedProjectId) {
      selectProject(selectedProjectId);
    } else {
      clearSelectedProject();
    }
  }, [selectedProjectId, selectProject, clearSelectedProject]);

  const handleProjectSelect = (projectId: string) => {
    setSelectedProjectId(projectId);
    setActivePanel("project_detail"); // Navigate to project detail view
  };

  const handleBackToProjects = () => {
    setSelectedProjectId(null);
    setActivePanel("projects");
  };

  const renderPanel = () => {
    switch (activePanel) {
      case "dashboard":
        return <DashboardOverview />;
      case "projects":
        return <ProjectDashboard onProjectSelect={handleProjectSelect} />;
      case "project_detail":
        return selectedProjectId ? (
          <ProjectDetailView
            projectId={selectedProjectId}
            onBack={handleBackToProjects}
          />
        ) : (
          <ProjectDashboard onProjectSelect={handleProjectSelect} />
        );
      case "antigravity":
        return <AntigravityPanel />;
      case "idea":
        return <IdeaAnalyzer />;
      case "patent":
        return <PatentRiskPanel />;
      case "research":
        return <ResearchPanel />;
      case "knowledge":
        return <KnowledgeGraphPanel />;
      case "roadmap":
        return selectedProjectId ? (
          <RoadmapCreator projectId={selectedProjectId} />
        ) : (
          <ProjectDashboard onProjectSelect={handleProjectSelect} />
        );
      case "pipeline":
        return selectedProjectId ? (
          <PipelineStatus projectId={selectedProjectId} />
        ) : (
          <ProjectDashboard onProjectSelect={handleProjectSelect} />
        );
      default:
        return <DashboardOverview />;
    }
  };

  return (
    <div className={styles.appContainer}>
      <Header />
      <div className={styles.mainContent}>
        <Sidebar
          activePanel={activePanel}
          setActivePanel={setActivePanel}
          selectedProject={selectedProject}
          onClearProject={() => setSelectedProjectId(null)}
        />
        <main className={styles.panelContainer}>
          <AnimatePresence mode="wait">
            <motion.div
              key={activePanel + (selectedProjectId || "")}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className={styles.panelWrapper}
            >
              {renderPanel()}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}


