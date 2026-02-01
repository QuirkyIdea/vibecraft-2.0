"use client";

import { useEffect } from "react";
import { motion } from "framer-motion";
import {
    CheckCircle,
    Circle,
    ChevronRight,
    Calendar,
    Flag,
    Sparkles
} from "lucide-react";
import { useProjects, RoadmapPhase, RoadmapMilestone } from "@/context/ProjectContext";
import styles from "./RoadmapCreator.module.css";

interface RoadmapCreatorProps {
    projectId: string;
}

export default function RoadmapCreator({ projectId }: RoadmapCreatorProps) {
    const { roadmap, fetchRoadmap, updateMilestone, selectedProject } = useProjects();

    useEffect(() => {
        if (projectId) {
            fetchRoadmap(projectId);
        }
    }, [projectId, fetchRoadmap]);

    const handleMilestoneToggle = (phaseId: string, milestoneId: string, currentCompleted: boolean) => {
        updateMilestone(projectId, phaseId, milestoneId, !currentCompleted);
    };

    const calculatePhaseProgress = (phase: RoadmapPhase): number => {
        if (phase.milestones.length === 0) return 0;
        const completed = phase.milestones.filter(m => m.completed).length;
        return Math.round((completed / phase.milestones.length) * 100);
    };

    const calculateOverallProgress = (): number => {
        if (!roadmap || roadmap.phases.length === 0) return 0;
        const allMilestones = roadmap.phases.flatMap(p => p.milestones);
        if (allMilestones.length === 0) return 0;
        const completed = allMilestones.filter(m => m.completed).length;
        return Math.round((completed / allMilestones.length) * 100);
    };

    if (!roadmap) {
        return (
            <div className={styles.loading}>
                <motion.div
                    className={styles.loadingOrb}
                    animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                />
                <p>Loading roadmap...</p>
            </div>
        );
    }

    const overallProgress = calculateOverallProgress();

    return (
        <div className={styles.container}>
            {/* Header */}
            <div className={styles.header}>
                <div className={styles.headerContent}>
                    <div className={styles.headerIcon}>
                        <Flag size={24} />
                    </div>
                    <div>
                        <h2>Project Roadmap</h2>
                        <p>{selectedProject?.title}</p>
                    </div>
                </div>
                <div className={styles.overallProgress}>
                    <div className={styles.progressCircle}>
                        <svg viewBox="0 0 36 36">
                            <path
                                className={styles.progressBg}
                                d="M18 2.0845
                                    a 15.9155 15.9155 0 0 1 0 31.831
                                    a 15.9155 15.9155 0 0 1 0 -31.831"
                            />
                            <motion.path
                                className={styles.progressFill}
                                d="M18 2.0845
                                    a 15.9155 15.9155 0 0 1 0 31.831
                                    a 15.9155 15.9155 0 0 1 0 -31.831"
                                initial={{ strokeDasharray: "0, 100" }}
                                animate={{ strokeDasharray: `${overallProgress}, 100` }}
                                transition={{ duration: 1 }}
                            />
                        </svg>
                        <span>{overallProgress}%</span>
                    </div>
                    <div className={styles.progressLabel}>
                        <strong>Overall Progress</strong>
                        <span>{roadmap.phases.flatMap(p => p.milestones).filter(m => m.completed).length} of {roadmap.phases.flatMap(p => p.milestones).length} tasks</span>
                    </div>
                </div>
            </div>

            {/* Phases */}
            <div className={styles.phases}>
                {roadmap.phases.map((phase, phaseIndex) => {
                    const phaseProgress = calculatePhaseProgress(phase);
                    const isComplete = phaseProgress === 100;

                    return (
                        <motion.div
                            key={phase.id}
                            className={styles.phase}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: phaseIndex * 0.1 }}
                        >
                            {/* Phase Header */}
                            <div className={styles.phaseHeader}>
                                <div
                                    className={styles.phaseIndicator}
                                    style={{ background: phase.color }}
                                >
                                    {isComplete ? (
                                        <CheckCircle size={20} />
                                    ) : (
                                        <span>{phaseIndex + 1}</span>
                                    )}
                                </div>
                                <div className={styles.phaseInfo}>
                                    <h3>{phase.name}</h3>
                                    <p>{phase.description}</p>
                                </div>
                                <div className={styles.phaseProgress}>
                                    <span>{phaseProgress}%</span>
                                    <div className={styles.phaseProgressBar}>
                                        <motion.div
                                            className={styles.phaseProgressFill}
                                            style={{ background: phase.color }}
                                            initial={{ width: 0 }}
                                            animate={{ width: `${phaseProgress}%` }}
                                            transition={{ duration: 0.5 }}
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Milestones */}
                            <div className={styles.milestones}>
                                {phase.milestones.map((milestone, milestoneIndex) => (
                                    <motion.div
                                        key={milestone.id}
                                        className={`${styles.milestone} ${milestone.completed ? styles.completed : ""}`}
                                        initial={{ opacity: 0, x: -10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: phaseIndex * 0.1 + milestoneIndex * 0.05 }}
                                    >
                                        <button
                                            className={styles.milestoneCheck}
                                            onClick={() => handleMilestoneToggle(phase.id, milestone.id, milestone.completed)}
                                            style={{ borderColor: phase.color }}
                                        >
                                            {milestone.completed ? (
                                                <motion.div
                                                    initial={{ scale: 0 }}
                                                    animate={{ scale: 1 }}
                                                    transition={{ type: "spring", stiffness: 300 }}
                                                >
                                                    <CheckCircle size={20} style={{ color: phase.color }} />
                                                </motion.div>
                                            ) : (
                                                <Circle size={20} />
                                            )}
                                        </button>
                                        <div className={styles.milestoneContent}>
                                            <h4>{milestone.title}</h4>
                                            <p>{milestone.description}</p>
                                        </div>
                                        {milestone.target_date && (
                                            <div className={styles.milestoneDate}>
                                                <Calendar size={14} />
                                                <span>{new Date(milestone.target_date).toLocaleDateString()}</span>
                                            </div>
                                        )}
                                    </motion.div>
                                ))}
                            </div>

                            {/* Connector */}
                            {phaseIndex < roadmap.phases.length - 1 && (
                                <div className={styles.connector}>
                                    <ChevronRight size={24} />
                                </div>
                            )}
                        </motion.div>
                    );
                })}
            </div>

            {/* Completion Message */}
            {overallProgress === 100 && (
                <motion.div
                    className={styles.completionBanner}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                >
                    <Sparkles size={24} />
                    <div>
                        <h3>Roadmap Complete!</h3>
                        <p>All milestones have been achieved. Great work!</p>
                    </div>
                </motion.div>
            )}
        </div>
    );
}
