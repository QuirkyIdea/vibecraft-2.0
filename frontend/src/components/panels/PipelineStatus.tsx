"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
    User,
    Brain,
    Users,
    Network,
    Search,
    FileOutput,
    CheckCircle,
    AlertCircle,
    ArrowRight,
    Zap
} from "lucide-react";
import { useProjects, PipelineNode } from "@/context/ProjectContext";
import styles from "./PipelineStatus.module.css";

interface PipelineStatusProps {
    projectId: string;
}

const nodeIcons: Record<string, React.ElementType> = {
    input: User,
    brain: Brain,
    agents: Users,
    knowledge: Network,
    engine: Search,
    output: FileOutput
};

const nodeDescriptions: Record<string, string> = {
    input: "Receiving and validating user input",
    brain: "AI processing and initial analysis",
    agents: "Coordinating specialized agents",
    knowledge: "Building relationships and graph",
    engine: "Deep analysis and scoring",
    output: "Generating structured results"
};

export default function PipelineStatus({ projectId }: PipelineStatusProps) {
    const { pipelineStatus, fetchPipelineStatus, selectedProject, analyzeProject, isLoading } = useProjects();
    const [isPolling, setIsPolling] = useState(false);

    useEffect(() => {
        if (projectId) {
            fetchPipelineStatus(projectId);
        }
    }, [projectId, fetchPipelineStatus]);

    // Poll for updates when analysis is in progress
    useEffect(() => {
        if (pipelineStatus &&
            pipelineStatus.current_stage !== "idle" &&
            pipelineStatus.current_stage !== "complete" &&
            pipelineStatus.current_stage !== "error") {
            const interval = setInterval(() => {
                fetchPipelineStatus(projectId);
            }, 2000);
            setIsPolling(true);
            return () => {
                clearInterval(interval);
                setIsPolling(false);
            };
        }
        setIsPolling(false);
    }, [pipelineStatus?.current_stage, projectId, fetchPipelineStatus]);

    const handleStartAnalysis = async () => {
        await analyzeProject(projectId);
        fetchPipelineStatus(projectId);
    };

    const getNodeIcon = (node: PipelineNode) => {
        const Icon = nodeIcons[node.id] || Brain;
        return <Icon size={20} />;
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case "complete":
                return "var(--success)";
            case "active":
                return "var(--accent-primary)";
            case "error":
                return "var(--error)";
            default:
                return "var(--text-muted)";
        }
    };

    if (!pipelineStatus) {
        return (
            <div className={styles.loading}>
                <motion.div
                    className={styles.loadingOrb}
                    animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                />
                <p>Loading pipeline status...</p>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            {/* Header */}
            <div className={styles.header}>
                <div className={styles.headerContent}>
                    <div className={styles.headerIcon}>
                        <Zap size={24} />
                    </div>
                    <div>
                        <h2>Analysis Pipeline</h2>
                        <p>Real-time processing visualization</p>
                    </div>
                </div>
                <div className={styles.overallStatus}>
                    <span className={styles.statusBadge} data-status={pipelineStatus.current_stage}>
                        {pipelineStatus.current_stage === "complete" ? (
                            <><CheckCircle size={16} /> Complete</>
                        ) : pipelineStatus.current_stage === "error" ? (
                            <><AlertCircle size={16} /> Error</>
                        ) : pipelineStatus.current_stage === "idle" ? (
                            "Ready"
                        ) : (
                            <>
                                <motion.div
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                    style={{ display: "inline-flex" }}
                                >
                                    <Brain size={16} />
                                </motion.div>
                                Processing
                            </>
                        )}
                    </span>
                </div>
            </div>

            {/* Progress Bar */}
            <div className={styles.progressSection}>
                <div className={styles.progressHeader}>
                    <span>Overall Progress</span>
                    <span>{Math.round(pipelineStatus.overall_progress)}%</span>
                </div>
                <div className={styles.progressBar}>
                    <motion.div
                        className={styles.progressFill}
                        initial={{ width: 0 }}
                        animate={{ width: `${pipelineStatus.overall_progress}%` }}
                        transition={{ duration: 0.5 }}
                    />
                </div>
            </div>

            {/* Pipeline Visualization */}
            <div className={styles.pipeline}>
                {pipelineStatus.nodes.map((node, index) => (
                    <div key={node.id} className={styles.nodeWrapper}>
                        <motion.div
                            className={`${styles.node} ${styles[node.status]}`}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: index * 0.1 }}
                        >
                            {/* Node Circle */}
                            <div
                                className={styles.nodeCircle}
                                style={{ borderColor: getStatusColor(node.status) }}
                            >
                                {node.status === "active" ? (
                                    <motion.div
                                        animate={{ scale: [1, 1.1, 1] }}
                                        transition={{ duration: 1, repeat: Infinity }}
                                        style={{ display: "flex" }}
                                    >
                                        {getNodeIcon(node)}
                                    </motion.div>
                                ) : (
                                    getNodeIcon(node)
                                )}

                                {/* Pulse effect for active nodes */}
                                {node.status === "active" && (
                                    <motion.div
                                        className={styles.pulse}
                                        animate={{ scale: [1, 2], opacity: [0.5, 0] }}
                                        transition={{ duration: 1.5, repeat: Infinity }}
                                    />
                                )}
                            </div>

                            {/* Node Info */}
                            <div className={styles.nodeInfo}>
                                <h4>{node.name}</h4>
                                <p>{nodeDescriptions[node.id] || node.message}</p>
                                {node.status === "active" && node.progress > 0 && (
                                    <div className={styles.nodeProgress}>
                                        <div className={styles.nodeProgressBar}>
                                            <motion.div
                                                className={styles.nodeProgressFill}
                                                animate={{ width: `${node.progress}%` }}
                                            />
                                        </div>
                                        <span>{Math.round(node.progress)}%</span>
                                    </div>
                                )}
                            </div>

                            {/* Status Indicator */}
                            <div className={styles.nodeStatus}>
                                {node.status === "complete" && (
                                    <CheckCircle size={18} className={styles.statusComplete} />
                                )}
                                {node.status === "error" && (
                                    <AlertCircle size={18} className={styles.statusError} />
                                )}
                            </div>
                        </motion.div>

                        {/* Connector Arrow */}
                        {index < pipelineStatus.nodes.length - 1 && (
                            <div className={styles.connector}>
                                <motion.div
                                    initial={{ opacity: 0.3 }}
                                    animate={{
                                        opacity: node.status === "complete" ? 1 : 0.3
                                    }}
                                >
                                    <ArrowRight size={20} />
                                </motion.div>
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {/* Action Section */}
            {pipelineStatus.current_stage === "idle" && (
                <div className={styles.actionSection}>
                    <p>Click the button below to start analyzing your project.</p>
                    <motion.button
                        className={styles.analyzeButton}
                        onClick={handleStartAnalysis}
                        disabled={isLoading}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                    >
                        {isLoading ? (
                            <motion.div
                                animate={{ rotate: 360 }}
                                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                            >
                                <Brain size={20} />
                            </motion.div>
                        ) : (
                            <Zap size={20} />
                        )}
                        <span>{isLoading ? "Analyzing..." : "Start Analysis"}</span>
                    </motion.button>
                </div>
            )}

            {/* Error Message */}
            {pipelineStatus.error_message && (
                <motion.div
                    className={styles.errorBanner}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <AlertCircle size={20} />
                    <div>
                        <strong>Analysis Error</strong>
                        <p>{pipelineStatus.error_message}</p>
                    </div>
                </motion.div>
            )}

            {/* Success Message */}
            {pipelineStatus.current_stage === "complete" && (
                <motion.div
                    className={styles.successBanner}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <CheckCircle size={20} />
                    <div>
                        <strong>Analysis Complete</strong>
                        <p>Your project has been analyzed successfully. Check the results in the project details.</p>
                    </div>
                </motion.div>
            )}
        </div>
    );
}
