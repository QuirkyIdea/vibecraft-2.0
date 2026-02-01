"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Plus,
    FileSearch,
    BookOpen,
    Clock,
    TrendingUp,
    Activity,
    AlertCircle,
    CheckCircle,
    XCircle,
    ChevronRight,
    MoreVertical,
    Trash2,
    ExternalLink
} from "lucide-react";
import { useProjects, ProjectCard as ProjectCardType, NoveltyStatus } from "@/context/ProjectContext";
import ProjectWizard from "@/components/ProjectWizard";
import styles from "./ProjectDashboard.module.css";

interface ProjectDashboardProps {
    onProjectSelect: (projectId: string) => void;
}

export default function ProjectDashboard({ onProjectSelect }: ProjectDashboardProps) {
    const { projects, fetchProjects, deleteProject, isLoading } = useProjects();
    const [showWizard, setShowWizard] = useState(false);
    const [activeMenu, setActiveMenu] = useState<string | null>(null);
    const [filter, setFilter] = useState<"all" | "patent" | "research">("all");

    useEffect(() => {
        fetchProjects();
    }, [fetchProjects]);

    const filteredProjects = projects.filter(p => {
        if (filter === "all") return true;
        return p.project_type === filter;
    });

    const patentCount = projects.filter(p => p.project_type === "patent").length;
    const researchCount = projects.filter(p => p.project_type === "research").length;

    const getStatusIcon = (status: NoveltyStatus) => {
        switch (status) {
            case "green":
                return <CheckCircle size={16} className={styles.statusGreen} />;
            case "yellow":
                return <AlertCircle size={16} className={styles.statusYellow} />;
            case "red":
                return <XCircle size={16} className={styles.statusRed} />;
            default:
                return <Activity size={16} className={styles.statusUnknown} />;
        }
    };

    const getStatusLabel = (status: NoveltyStatus) => {
        switch (status) {
            case "green":
                return "High Novelty";
            case "yellow":
                return "Moderate Risk";
            case "red":
                return "High Risk";
            default:
                return "Not Analyzed";
        }
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

        if (days === 0) return "Today";
        if (days === 1) return "Yesterday";
        if (days < 7) return `${days} days ago`;
        return date.toLocaleDateString();
    };

    const handleDelete = async (projectId: string) => {
        if (window.confirm("Are you sure you want to delete this project?")) {
            await deleteProject(projectId);
        }
        setActiveMenu(null);
    };

    return (
        <div className={styles.dashboard}>
            {/* Header */}
            <div className={styles.header}>
                <div className={styles.headerContent}>
                    <h1>Your Projects</h1>
                    <p>Manage your patent and research projects</p>
                </div>
                <motion.button
                    className={styles.createButton}
                    onClick={() => setShowWizard(true)}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                >
                    <Plus size={20} />
                    <span>New Project</span>
                </motion.button>
            </div>

            {/* Stats */}
            <div className={styles.stats}>
                <div className={styles.statCard}>
                    <div className={styles.statIcon} style={{ background: "linear-gradient(135deg, #6366f1, #8b5cf6)" }}>
                        <FileSearch size={20} />
                    </div>
                    <div className={styles.statContent}>
                        <span className={styles.statValue}>{patentCount}</span>
                        <span className={styles.statLabel}>Patent Projects</span>
                    </div>
                </div>
                <div className={styles.statCard}>
                    <div className={styles.statIcon} style={{ background: "linear-gradient(135deg, #06b6d4, #14b8a6)" }}>
                        <BookOpen size={20} />
                    </div>
                    <div className={styles.statContent}>
                        <span className={styles.statValue}>{researchCount}</span>
                        <span className={styles.statLabel}>Research Projects</span>
                    </div>
                </div>
                <div className={styles.statCard}>
                    <div className={styles.statIcon} style={{ background: "linear-gradient(135deg, #22c55e, #16a34a)" }}>
                        <TrendingUp size={20} />
                    </div>
                    <div className={styles.statContent}>
                        <span className={styles.statValue}>
                            {projects.filter(p => p.novelty_status === "green").length}
                        </span>
                        <span className={styles.statLabel}>High Novelty</span>
                    </div>
                </div>
            </div>

            {/* Filters */}
            <div className={styles.filters}>
                <button
                    className={`${styles.filterButton} ${filter === "all" ? styles.active : ""}`}
                    onClick={() => setFilter("all")}
                >
                    All Projects
                </button>
                <button
                    className={`${styles.filterButton} ${filter === "patent" ? styles.active : ""}`}
                    onClick={() => setFilter("patent")}
                >
                    <FileSearch size={16} />
                    Patent
                </button>
                <button
                    className={`${styles.filterButton} ${filter === "research" ? styles.active : ""}`}
                    onClick={() => setFilter("research")}
                >
                    <BookOpen size={16} />
                    Research
                </button>
            </div>

            {/* Projects Grid */}
            {isLoading ? (
                <div className={styles.loadingState}>
                    <motion.div
                        className={styles.loadingOrb}
                        animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                    />
                    <p>Loading projects...</p>
                </div>
            ) : filteredProjects.length === 0 ? (
                <motion.div
                    className={styles.emptyState}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <div className={styles.emptyIcon}>
                        <Plus size={40} />
                    </div>
                    <h3>No projects yet</h3>
                    <p>Create your first project to start analyzing ideas</p>
                    <button className={styles.emptyButton} onClick={() => setShowWizard(true)}>
                        Create Project
                    </button>
                </motion.div>
            ) : (
                <div className={styles.projectsGrid}>
                    <AnimatePresence>
                        {filteredProjects.map((project, index) => (
                            <motion.div
                                key={project.id}
                                className={styles.projectCard}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, scale: 0.95 }}
                                transition={{ delay: index * 0.05 }}
                                onClick={() => onProjectSelect(project.id)}
                            >
                                {/* Card Header */}
                                <div className={styles.cardHeader}>
                                    <div
                                        className={styles.projectTypeIcon}
                                        style={{
                                            background: project.project_type === "patent"
                                                ? "linear-gradient(135deg, #6366f1, #8b5cf6)"
                                                : "linear-gradient(135deg, #06b6d4, #14b8a6)"
                                        }}
                                    >
                                        {project.project_type === "patent" ? (
                                            <FileSearch size={18} />
                                        ) : (
                                            <BookOpen size={18} />
                                        )}
                                    </div>
                                    <div className={styles.cardMenu}>
                                        <button
                                            className={styles.menuButton}
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                setActiveMenu(activeMenu === project.id ? null : project.id);
                                            }}
                                        >
                                            <MoreVertical size={18} />
                                        </button>
                                        {activeMenu === project.id && (
                                            <div className={styles.menuDropdown}>
                                                <button onClick={(e) => {
                                                    e.stopPropagation();
                                                    onProjectSelect(project.id);
                                                }}>
                                                    <ExternalLink size={14} />
                                                    Open
                                                </button>
                                                <button
                                                    className={styles.deleteButton}
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleDelete(project.id);
                                                    }}
                                                >
                                                    <Trash2 size={14} />
                                                    Delete
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* Card Content */}
                                <h3 className={styles.cardTitle}>{project.title}</h3>
                                <span className={styles.cardType}>
                                    {project.project_type === "patent" ? "Patent Project" : "Research Project"}
                                </span>

                                {/* Novelty Status */}
                                <div className={`${styles.noveltyStatus} ${styles[project.novelty_status]}`}>
                                    {getStatusIcon(project.novelty_status)}
                                    <span>{getStatusLabel(project.novelty_status)}</span>
                                </div>

                                {/* Progress */}
                                <div className={styles.progressSection}>
                                    <div className={styles.progressHeader}>
                                        <span>Progress</span>
                                        <span>{Math.round(project.progress)}%</span>
                                    </div>
                                    <div className={styles.progressBar}>
                                        <motion.div
                                            className={styles.progressFill}
                                            initial={{ width: 0 }}
                                            animate={{ width: `${project.progress}%` }}
                                            transition={{ duration: 0.5 }}
                                        />
                                    </div>
                                </div>

                                {/* Footer */}
                                <div className={styles.cardFooter}>
                                    <div className={styles.timestamp}>
                                        <Clock size={14} />
                                        <span>
                                            {project.last_analyzed
                                                ? `Analyzed ${formatDate(project.last_analyzed)}`
                                                : `Created ${formatDate(project.created_at)}`}
                                        </span>
                                    </div>
                                    <ChevronRight size={18} className={styles.arrow} />
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                </div>
            )}

            {/* Project Creation Wizard */}
            <ProjectWizard
                isOpen={showWizard}
                onClose={() => setShowWizard(false)}
                onSuccess={(projectId) => {
                    fetchProjects();
                    onProjectSelect(projectId);
                }}
            />
        </div>
    );
}
