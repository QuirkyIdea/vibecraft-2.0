"use client";

import { motion } from "framer-motion";
import {
    LayoutDashboard,
    Lightbulb,
    FileSearch,
    BookOpen,
    Network,
    AlertTriangle,
    FolderKanban,
    Flag,
    Activity,
    X,
    ChevronRight,
    Rocket,
} from "lucide-react";
import { PanelType } from "@/app/page";
import { Project } from "@/context/ProjectContext";
import styles from "./Sidebar.module.css";

interface SidebarProps {
    activePanel: PanelType;
    setActivePanel: (panel: PanelType) => void;
    selectedProject?: Project | null;
    onClearProject?: () => void;
}

const mainNavItems = [
    { id: "dashboard" as PanelType, label: "Dashboard", icon: LayoutDashboard },
    { id: "projects" as PanelType, label: "My Projects", icon: FolderKanban },
];

const toolNavItems = [
    { id: "antigravity" as PanelType, label: "Full Analysis", icon: Rocket, highlight: true },
    { id: "idea" as PanelType, label: "Idea Analyzer", icon: Lightbulb },
    { id: "patent" as PanelType, label: "Patent Risk", icon: FileSearch },
    { id: "research" as PanelType, label: "Research", icon: BookOpen },
    { id: "knowledge" as PanelType, label: "Knowledge Graph", icon: Network },
];

const projectNavItems = [
    { id: "roadmap" as PanelType, label: "Roadmap", icon: Flag },
    { id: "pipeline" as PanelType, label: "Pipeline Status", icon: Activity },
];

export default function Sidebar({
    activePanel,
    setActivePanel,
    selectedProject,
    onClearProject
}: SidebarProps) {
    return (
        <aside className={styles.sidebar}>
            <nav className={styles.nav}>
                {/* Main Navigation */}
                <div className={styles.navSection}>
                    <span className={styles.sectionLabel}>Main</span>
                    {mainNavItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = activePanel === item.id;

                        return (
                            <button
                                key={item.id}
                                className={`${styles.navItem} ${isActive ? styles.active : ""}`}
                                onClick={() => setActivePanel(item.id)}
                            >
                                {isActive && (
                                    <motion.div
                                        className={styles.activeIndicator}
                                        layoutId="activeIndicator"
                                        transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                    />
                                )}
                                <Icon size={20} className={styles.navIcon} />
                                <span>{item.label}</span>
                            </button>
                        );
                    })}
                </div>

                {/* Selected Project Context */}
                {selectedProject && (
                    <div className={styles.navSection}>
                        <span className={styles.sectionLabel}>Active Project</span>
                        <div className={styles.projectContext}>
                            <div className={styles.projectInfo}>
                                <span className={styles.projectTitle}>{selectedProject.title}</span>
                                <span className={styles.projectType}>
                                    {selectedProject.project_type === "patent" ? "Patent" : "Research"}
                                </span>
                            </div>
                            <button
                                className={styles.clearProject}
                                onClick={onClearProject}
                                title="Clear project selection"
                            >
                                <X size={16} />
                            </button>
                        </div>
                        {projectNavItems.map((item) => {
                            const Icon = item.icon;
                            const isActive = activePanel === item.id;

                            return (
                                <button
                                    key={item.id}
                                    className={`${styles.navItem} ${isActive ? styles.active : ""}`}
                                    onClick={() => setActivePanel(item.id)}
                                >
                                    {isActive && (
                                        <motion.div
                                            className={styles.activeIndicator}
                                            layoutId="activeIndicator"
                                            transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                        />
                                    )}
                                    <Icon size={20} className={styles.navIcon} />
                                    <span>{item.label}</span>
                                    <ChevronRight size={16} className={styles.navArrow} />
                                </button>
                            );
                        })}
                    </div>
                )}

                {/* Tools Navigation */}
                <div className={styles.navSection}>
                    <span className={styles.sectionLabel}>Analysis Tools</span>
                    {toolNavItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = activePanel === item.id;
                        const isHighlight = 'highlight' in item && item.highlight;

                        return (
                            <button
                                key={item.id}
                                className={`${styles.navItem} ${isActive ? styles.active : ""} ${isHighlight ? styles.navItemHighlight : ""}`}
                                onClick={() => setActivePanel(item.id)}
                            >
                                {isActive && (
                                    <motion.div
                                        className={styles.activeIndicator}
                                        layoutId="activeIndicator"
                                        transition={{ type: "spring", stiffness: 300, damping: 30 }}
                                    />
                                )}
                                <Icon size={20} className={styles.navIcon} />
                                <span>{item.label}</span>
                            </button>
                        );
                    })}
                </div>
            </nav>

            <div className={styles.bottomSection}>
                <div className={styles.disclaimer}>
                    <AlertTriangle size={16} />
                    <div className={styles.disclaimerText}>
                        <strong>Legal Notice</strong>
                        <p>This system provides probabilistic indicators only. Not legal advice.</p>
                    </div>
                </div>
            </div>
        </aside>
    );
}

