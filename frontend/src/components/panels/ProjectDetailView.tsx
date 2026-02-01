"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    ArrowLeft,
    FileText,
    Lightbulb,
    Shield,
    AlertTriangle,
    CheckCircle,
    XCircle,
    TrendingUp,
    Clock,
    Tag,
    Beaker,
    Scale,
    Target,
    FileSearch,
    BookOpen,
    Brain,
    ChevronDown,
    ChevronRight,
    Zap,
    BarChart3,
    PieChart,
    Activity
} from "lucide-react";
import { useProjects, Project } from "@/context/ProjectContext";
import styles from "./ProjectDetailView.module.css";

interface ProjectDetailViewProps {
    projectId: string;
    onBack: () => void;
}

interface AnalysisSection {
    id: string;
    title: string;
    icon: React.ElementType;
    color: string;
}

const analysisSections: AnalysisSection[] = [
    { id: "overview", title: "Project Overview", icon: FileText, color: "#6366f1" },
    { id: "novelty", title: "Novelty Assessment", icon: Lightbulb, color: "#22c55e" },
    { id: "claims", title: "Novel Claims", icon: Target, color: "#8b5cf6" },
    { id: "prior_art", title: "Prior Art Analysis", icon: FileSearch, color: "#f59e0b" },
    { id: "patent_risk", title: "Patent Risk Assessment", icon: Shield, color: "#ef4444" },
    { id: "recommendations", title: "Recommendations", icon: Beaker, color: "#06b6d4" }
];

export default function ProjectDetailView({ projectId, onBack }: ProjectDetailViewProps) {
    const { selectedProject, selectProject, analyzeProject, isLoading } = useProjects();
    const [expandedSections, setExpandedSections] = useState<Set<string>>(
        new Set(["overview", "novelty", "claims"])
    );
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    useEffect(() => {
        if (projectId) {
            selectProject(projectId);
        }
    }, [projectId, selectProject]);

    const toggleSection = (sectionId: string) => {
        const newExpanded = new Set(expandedSections);
        if (newExpanded.has(sectionId)) {
            newExpanded.delete(sectionId);
        } else {
            newExpanded.add(sectionId);
        }
        setExpandedSections(newExpanded);
    };

    const handleAnalyze = async () => {
        if (!projectId) return;
        setIsAnalyzing(true);
        await analyzeProject(projectId);
        await selectProject(projectId); // Refresh project data
        setIsAnalyzing(false);
    };

    const getNoveltyColor = (score: number): string => {
        if (score >= 70) return "var(--success)";
        if (score >= 40) return "var(--warning)";
        return "var(--error)";
    };

    const getRiskColor = (level: string): string => {
        switch (level?.toLowerCase()) {
            case "low": return "var(--success)";
            case "medium": return "var(--warning)";
            case "high": return "var(--error)";
            default: return "var(--text-muted)";
        }
    };

    if (isLoading && !selectedProject) {
        return (
            <div className={styles.loading}>
                <motion.div
                    className={styles.loadingOrb}
                    animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                />
                <p>Loading project details...</p>
            </div>
        );
    }

    if (!selectedProject) {
        return (
            <div className={styles.notFound}>
                <AlertTriangle size={48} />
                <h2>Project Not Found</h2>
                <p>The requested project could not be loaded.</p>
                <button onClick={onBack} className={styles.backButton}>
                    <ArrowLeft size={18} />
                    Back to Projects
                </button>
            </div>
        );
    }

    const analysis = selectedProject.analysis;
    const hasAnalysis = !!analysis;

    return (
        <div className={styles.container}>
            {/* Header */}
            <div className={styles.header}>
                <button onClick={onBack} className={styles.backBtn}>
                    <ArrowLeft size={20} />
                    <span>Back to Projects</span>
                </button>
                <div className={styles.headerInfo}>
                    <div className={styles.projectType} data-type={selectedProject.project_type}>
                        {selectedProject.project_type === "patent" ? (
                            <><Shield size={16} /> Patent</>
                        ) : (
                            <><BookOpen size={16} /> Research</>
                        )}
                    </div>
                    <h1>{selectedProject.title}</h1>
                    <p>{selectedProject.description}</p>
                </div>
                <div className={styles.headerActions}>
                    {!hasAnalysis ? (
                        <motion.button
                            className={styles.analyzeBtn}
                            onClick={handleAnalyze}
                            disabled={isAnalyzing}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                        >
                            {isAnalyzing ? (
                                <>
                                    <motion.div
                                        animate={{ rotate: 360 }}
                                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                    >
                                        <Brain size={20} />
                                    </motion.div>
                                    Analyzing...
                                </>
                            ) : (
                                <>
                                    <Zap size={20} />
                                    Run Full Analysis
                                </>
                            )}
                        </motion.button>
                    ) : (
                        <div className={styles.analyzedBadge}>
                            <CheckCircle size={18} />
                            Analysis Complete
                        </div>
                    )}
                </div>
            </div>

            {/* Score Cards */}
            {hasAnalysis && (
                <div className={styles.scoreCards}>
                    {/* Novelty Score */}
                    <motion.div
                        className={styles.scoreCard}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                    >
                        <div className={styles.scoreIcon} style={{ background: "rgba(34, 197, 94, 0.15)", color: "var(--success)" }}>
                            <Lightbulb size={24} />
                        </div>
                        <div className={styles.scoreContent}>
                            <span className={styles.scoreLabel}>Novelty Score</span>
                            <div className={styles.scoreValue}>
                                <span style={{ color: getNoveltyColor(analysis.novelty_score || 0) }}>
                                    {analysis.novelty_score || 0}%
                                </span>
                            </div>
                            <div className={styles.scoreBar}>
                                <div
                                    className={styles.scoreBarFill}
                                    style={{
                                        width: `${analysis.novelty_score || 0}%`,
                                        background: getNoveltyColor(analysis.novelty_score || 0)
                                    }}
                                />
                            </div>
                        </div>
                    </motion.div>

                    {/* Confidence */}
                    <motion.div
                        className={styles.scoreCard}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                    >
                        <div className={styles.scoreIcon} style={{ background: "rgba(99, 102, 241, 0.15)", color: "var(--accent-primary)" }}>
                            <BarChart3 size={24} />
                        </div>
                        <div className={styles.scoreContent}>
                            <span className={styles.scoreLabel}>Confidence Level</span>
                            <div className={styles.scoreValue}>
                                <span>{analysis.confidence_score || 0}%</span>
                            </div>
                            <div className={styles.scoreBar}>
                                <div
                                    className={styles.scoreBarFill}
                                    style={{ width: `${analysis.confidence_score || 0}%` }}
                                />
                            </div>
                        </div>
                    </motion.div>

                    {/* Patent Risk */}
                    <motion.div
                        className={styles.scoreCard}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                    >
                        <div className={styles.scoreIcon} style={{ background: "rgba(239, 68, 68, 0.15)", color: "var(--error)" }}>
                            <Shield size={24} />
                        </div>
                        <div className={styles.scoreContent}>
                            <span className={styles.scoreLabel}>Patent Risk</span>
                            <div className={styles.scoreValue}>
                                <span
                                    className={styles.riskBadge}
                                    style={{ color: getRiskColor(analysis.risk_level || "unknown") }}
                                >
                                    {analysis.risk_level || "Unknown"}
                                </span>
                            </div>
                        </div>
                    </motion.div>

                    {/* Prior Art Matches */}
                    <motion.div
                        className={styles.scoreCard}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 }}
                    >
                        <div className={styles.scoreIcon} style={{ background: "rgba(245, 158, 11, 0.15)", color: "var(--warning)" }}>
                            <FileSearch size={24} />
                        </div>
                        <div className={styles.scoreContent}>
                            <span className={styles.scoreLabel}>Prior Art Found</span>
                            <div className={styles.scoreValue}>
                                <span>{analysis.prior_art_matches?.length || 0}</span>
                            </div>
                            <span className={styles.scoreSubtext}>references</span>
                        </div>
                    </motion.div>
                </div>
            )}

            {/* Analysis Sections */}
            {hasAnalysis ? (
                <div className={styles.sections}>
                    {/* Novel Claims Section */}
                    <motion.div
                        className={styles.section}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.2 }}
                    >
                        <button
                            className={styles.sectionHeader}
                            onClick={() => toggleSection("claims")}
                        >
                            <div className={styles.sectionTitle}>
                                <Target size={20} style={{ color: "#8b5cf6" }} />
                                <h3>Novel Claims ({analysis.novel_claims?.length || 0})</h3>
                            </div>
                            {expandedSections.has("claims") ? (
                                <ChevronDown size={20} />
                            ) : (
                                <ChevronRight size={20} />
                            )}
                        </button>
                        <AnimatePresence>
                            {expandedSections.has("claims") && (
                                <motion.div
                                    className={styles.sectionContent}
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: "auto", opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    transition={{ duration: 0.2 }}
                                >
                                    {analysis.novel_claims && analysis.novel_claims.length > 0 ? (
                                        <div className={styles.claimsList}>
                                            {analysis.novel_claims.map((claim: any, idx: number) => (
                                                <div key={idx} className={styles.claimItem}>
                                                    <div className={styles.claimNumber}>{idx + 1}</div>
                                                    <div className={styles.claimContent}>
                                                        <p className={styles.claimText}>{claim.claim || claim}</p>
                                                        {claim.evidence && (
                                                            <div className={styles.claimEvidence}>
                                                                <Tag size={14} />
                                                                <span>{claim.evidence}</span>
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <p className={styles.noData}>No novel claims identified</p>
                                    )}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </motion.div>

                    {/* Prior Art Section */}
                    <motion.div
                        className={styles.section}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.3 }}
                    >
                        <button
                            className={styles.sectionHeader}
                            onClick={() => toggleSection("prior_art")}
                        >
                            <div className={styles.sectionTitle}>
                                <FileSearch size={20} style={{ color: "#f59e0b" }} />
                                <h3>Prior Art Matches ({analysis.prior_art_matches?.length || 0})</h3>
                            </div>
                            {expandedSections.has("prior_art") ? (
                                <ChevronDown size={20} />
                            ) : (
                                <ChevronRight size={20} />
                            )}
                        </button>
                        <AnimatePresence>
                            {expandedSections.has("prior_art") && (
                                <motion.div
                                    className={styles.sectionContent}
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: "auto", opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    transition={{ duration: 0.2 }}
                                >
                                    {analysis.prior_art_matches && analysis.prior_art_matches.length > 0 ? (
                                        <div className={styles.priorArtList}>
                                            {analysis.prior_art_matches.map((match: any, idx: number) => (
                                                <div key={idx} className={styles.priorArtItem}>
                                                    <div className={styles.priorArtHeader}>
                                                        <span className={styles.priorArtTitle}>
                                                            {match.title || match.patent_id || `Reference ${idx + 1}`}
                                                        </span>
                                                        <span
                                                            className={styles.similarityBadge}
                                                            style={{
                                                                background: match.similarity > 70
                                                                    ? "rgba(239, 68, 68, 0.15)"
                                                                    : "rgba(245, 158, 11, 0.15)",
                                                                color: match.similarity > 70
                                                                    ? "var(--error)"
                                                                    : "var(--warning)"
                                                            }}
                                                        >
                                                            {match.similarity || match.relevance || 0}% similar
                                                        </span>
                                                    </div>
                                                    {match.summary && (
                                                        <p className={styles.priorArtSummary}>{match.summary}</p>
                                                    )}
                                                    {match.overlap_areas && (
                                                        <div className={styles.overlapAreas}>
                                                            <strong>Overlap Areas:</strong>
                                                            <ul>
                                                                {match.overlap_areas.map((area: string, i: number) => (
                                                                    <li key={i}>{area}</li>
                                                                ))}
                                                            </ul>
                                                        </div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className={styles.noDataPositive}>
                                            <CheckCircle size={20} />
                                            <span>No significant prior art conflicts found</span>
                                        </div>
                                    )}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </motion.div>

                    {/* Risk Assessment Section */}
                    <motion.div
                        className={styles.section}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.4 }}
                    >
                        <button
                            className={styles.sectionHeader}
                            onClick={() => toggleSection("patent_risk")}
                        >
                            <div className={styles.sectionTitle}>
                                <Shield size={20} style={{ color: "#ef4444" }} />
                                <h3>Patent Risk Assessment</h3>
                            </div>
                            {expandedSections.has("patent_risk") ? (
                                <ChevronDown size={20} />
                            ) : (
                                <ChevronRight size={20} />
                            )}
                        </button>
                        <AnimatePresence>
                            {expandedSections.has("patent_risk") && (
                                <motion.div
                                    className={styles.sectionContent}
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: "auto", opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    transition={{ duration: 0.2 }}
                                >
                                    <div className={styles.riskGrid}>
                                        <div className={styles.riskCard}>
                                            <h4>Overall Risk Level</h4>
                                            <div
                                                className={styles.riskLevel}
                                                style={{ color: getRiskColor(analysis.risk_level || "unknown") }}
                                            >
                                                {analysis.risk_level?.toUpperCase() || "UNKNOWN"}
                                            </div>
                                        </div>
                                        {analysis.risk_factors && (
                                            <div className={styles.riskCard}>
                                                <h4>Risk Factors</h4>
                                                <ul className={styles.riskFactors}>
                                                    {analysis.risk_factors.map((factor: string, idx: number) => (
                                                        <li key={idx}>
                                                            <AlertTriangle size={14} />
                                                            {factor}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                    </div>
                                    {analysis.risk_summary && (
                                        <div className={styles.riskSummary}>
                                            <p>{analysis.risk_summary}</p>
                                        </div>
                                    )}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </motion.div>

                    {/* Recommendations Section */}
                    <motion.div
                        className={styles.section}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.5 }}
                    >
                        <button
                            className={styles.sectionHeader}
                            onClick={() => toggleSection("recommendations")}
                        >
                            <div className={styles.sectionTitle}>
                                <Beaker size={20} style={{ color: "#06b6d4" }} />
                                <h3>Recommendations</h3>
                            </div>
                            {expandedSections.has("recommendations") ? (
                                <ChevronDown size={20} />
                            ) : (
                                <ChevronRight size={20} />
                            )}
                        </button>
                        <AnimatePresence>
                            {expandedSections.has("recommendations") && (
                                <motion.div
                                    className={styles.sectionContent}
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: "auto", opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    transition={{ duration: 0.2 }}
                                >
                                    {analysis.recommendations && analysis.recommendations.length > 0 ? (
                                        <div className={styles.recommendationsList}>
                                            {analysis.recommendations.map((rec: any, idx: number) => (
                                                <div key={idx} className={styles.recommendationItem}>
                                                    <div className={styles.recIcon}>
                                                        <TrendingUp size={18} />
                                                    </div>
                                                    <div className={styles.recContent}>
                                                        <h4>{rec.title || `Recommendation ${idx + 1}`}</h4>
                                                        <p>{rec.description || rec}</p>
                                                        {rec.priority && (
                                                            <span className={styles.recPriority} data-priority={rec.priority}>
                                                                {rec.priority} priority
                                                            </span>
                                                        )}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <p className={styles.noData}>No specific recommendations at this time</p>
                                    )}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </motion.div>

                    {/* Full Analysis Summary */}
                    {analysis.summary && (
                        <motion.div
                            className={styles.section}
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.6 }}
                        >
                            <button
                                className={styles.sectionHeader}
                                onClick={() => toggleSection("summary")}
                            >
                                <div className={styles.sectionTitle}>
                                    <Brain size={20} style={{ color: "#6366f1" }} />
                                    <h3>AI Analysis Summary</h3>
                                </div>
                                {expandedSections.has("summary") ? (
                                    <ChevronDown size={20} />
                                ) : (
                                    <ChevronRight size={20} />
                                )}
                            </button>
                            <AnimatePresence>
                                {expandedSections.has("summary") && (
                                    <motion.div
                                        className={styles.sectionContent}
                                        initial={{ height: 0, opacity: 0 }}
                                        animate={{ height: "auto", opacity: 1 }}
                                        exit={{ height: 0, opacity: 0 }}
                                        transition={{ duration: 0.2 }}
                                    >
                                        <div className={styles.summaryContent}>
                                            <p>{analysis.summary}</p>
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </motion.div>
                    )}
                </div>
            ) : (
                /* No Analysis Yet */
                <div className={styles.noAnalysis}>
                    <div className={styles.noAnalysisIcon}>
                        <Brain size={48} />
                    </div>
                    <h2>No Analysis Yet</h2>
                    <p>Run a full analysis to see novelty assessment, patent risks, prior art matches, and recommendations.</p>
                    <motion.button
                        className={styles.analyzeBtn}
                        onClick={handleAnalyze}
                        disabled={isAnalyzing}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                    >
                        {isAnalyzing ? (
                            <>
                                <motion.div
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                >
                                    <Brain size={20} />
                                </motion.div>
                                Analyzing...
                            </>
                        ) : (
                            <>
                                <Zap size={20} />
                                Run Full Analysis
                            </>
                        )}
                    </motion.button>
                </div>
            )}

            {/* Metadata Footer */}
            <div className={styles.metadata}>
                <div className={styles.metaItem}>
                    <Clock size={14} />
                    <span>Created: {new Date(selectedProject.created_at).toLocaleDateString()}</span>
                </div>
                {selectedProject.last_analyzed && (
                    <div className={styles.metaItem}>
                        <Activity size={14} />
                        <span>Last analyzed: {new Date(selectedProject.last_analyzed).toLocaleString()}</span>
                    </div>
                )}
            </div>
        </div>
    );
}
