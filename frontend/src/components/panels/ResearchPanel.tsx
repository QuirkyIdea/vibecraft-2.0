"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    BookOpen,
    Send,
    Loader2,
    AlertTriangle,
    CheckCircle,
    XCircle,
    Lightbulb,
    Target,
    TrendingUp,
    Beaker,
    ChevronRight,
} from "lucide-react";
import PDFUpload from "@/components/PDFUpload";
import styles from "./ResearchPanel.module.css";

interface RelatedTopic {
    topic: string;
    relevance: string;
    description: string;
}

interface ResearchGap {
    gap: string;
    opportunity: string;
    difficulty: string;
}

interface ResearchDirection {
    direction: string;
    rationale: string;
    potential_impact: string;
}

interface ResearchResult {
    query_summary: string;
    key_concepts: string[];
    related_topics: RelatedTopic[];
    research_gaps: ResearchGap[];
    suggested_directions: ResearchDirection[];
    methodology_suggestions: string[];
    potential_challenges: string[];
    confidence: string;
    scope_disclaimer: string;
    unknowns: string[];
}

interface CrashLog {
    status: "CRASH";
    error_type: string;
    error_message: string;
    failed_stage: string;
    recommended_action: string;
}

export default function ResearchPanel() {
    const [query, setQuery] = useState("");
    const [domain, setDomain] = useState("");
    const [researchType, setResearchType] = useState("general");
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [result, setResult] = useState<ResearchResult | null>(null);
    const [error, setError] = useState<CrashLog | null>(null);

    const analyzeResearch = async () => {
        if (!query.trim() || query.length < 10) return;

        setIsAnalyzing(true);
        setResult(null);
        setError(null);

        try {
            const response = await fetch("http://localhost:8000/api/research/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    query: query,
                    domain: domain || undefined,
                    research_type: researchType,
                }),
            });

            const data = await response.json();

            if (data.status === "CRASH") {
                setError(data as CrashLog);
            } else {
                setResult(data as ResearchResult);
            }
        } catch (err) {
            setError({
                status: "CRASH",
                error_type: "UNKNOWN_FAILURE",
                error_message: "Failed to connect to the API. Is the backend running?",
                failed_stage: "retrieval",
                recommended_action: "system_debug",
            });
        } finally {
            setIsAnalyzing(false);
        }
    };

    const getRelevanceColor = (relevance: string) => {
        switch (relevance.toUpperCase()) {
            case "HIGH":
                return "var(--success)";
            case "MEDIUM":
                return "var(--warning)";
            case "LOW":
                return "var(--text-muted)";
            default:
                return "var(--text-secondary)";
        }
    };

    const getDifficultyColor = (difficulty: string) => {
        switch (difficulty.toUpperCase()) {
            case "HIGH":
                return "var(--error)";
            case "MEDIUM":
                return "var(--warning)";
            case "LOW":
                return "var(--success)";
            default:
                return "var(--text-secondary)";
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <div className={styles.headerIcon}>
                    <BookOpen size={24} />
                </div>
                <div>
                    <h1>Research Engine</h1>
                    <p>AI-powered research analysis and direction finding</p>
                </div>
            </div>

            <div className={styles.mainContent}>
                <div className={styles.inputSection}>
                    <div className={styles.card}>
                        <h3>Research Query</h3>

                        {/* PDF Upload */}
                        <div className={styles.inputGroup}>
                            <label className="label">Upload Research PDF (optional)</label>
                            <PDFUpload
                                onTextExtracted={(text) => {
                                    setQuery(prev => prev + (prev ? "\n\n" : "") + text);
                                }}
                                compact
                            />
                        </div>

                        <div className={styles.divider}>
                            <span>or enter topic manually</span>
                        </div>

                        <div className={styles.inputGroup}>
                            <label className="label">Research Topic or Question *</label>
                            <textarea
                                className={`input ${styles.queryInput}`}
                                placeholder="Describe your research topic, question, or area of interest. Be specific about what you want to explore."
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                            />
                            <span className={styles.charCount}>{query.length} characters (min 10)</span>
                        </div>

                        <div className={styles.inputRow}>
                            <div className={styles.inputGroup}>
                                <label className="label">Domain</label>
                                <input
                                    className="input"
                                    placeholder="e.g., AI, Biotech, Materials Science"
                                    value={domain}
                                    onChange={(e) => setDomain(e.target.value)}
                                />
                            </div>
                            <div className={styles.inputGroup}>
                                <label className="label">Analysis Type</label>
                                <select
                                    className="input"
                                    value={researchType}
                                    onChange={(e) => setResearchType(e.target.value)}
                                >
                                    <option value="general">General Analysis</option>
                                    <option value="literature_review">Literature Review</option>
                                    <option value="gap_analysis">Gap Analysis</option>
                                    <option value="trend_analysis">Trend Analysis</option>
                                </select>
                            </div>
                        </div>

                        <button
                            className={`btn btn-primary ${styles.analyzeBtn}`}
                            onClick={analyzeResearch}
                            disabled={isAnalyzing || query.length < 10}
                        >
                            {isAnalyzing ? (
                                <>
                                    <Loader2 size={18} className={styles.spinner} />
                                    Analyzing...
                                </>
                            ) : (
                                <>
                                    <Send size={18} />
                                    Analyze Research
                                </>
                            )}
                        </button>

                        <div className={styles.disclaimer}>
                            <AlertTriangle size={14} />
                            <span>
                                This provides AI-generated research guidance. Always verify with actual academic sources.
                            </span>
                        </div>
                    </div>
                </div>

                <div className={styles.resultsSection}>
                    <AnimatePresence mode="wait">
                        {isAnalyzing && (
                            <motion.div
                                key="loading"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className={styles.loadingState}
                            >
                                <div className={styles.loadingAnimation}>
                                    <motion.div
                                        className={styles.loadingBook}
                                        animate={{
                                            rotateY: [0, 180, 360],
                                        }}
                                        transition={{ duration: 2, repeat: Infinity }}
                                    >
                                        <BookOpen size={48} />
                                    </motion.div>
                                </div>
                                <p>Analyzing research landscape...</p>
                                <span className={styles.loadingSubtext}>
                                    Identifying gaps, trends, and opportunities
                                </span>
                            </motion.div>
                        )}

                        {error && !isAnalyzing && (
                            <motion.div
                                key="error"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0 }}
                                className={`${styles.card} ${styles.errorCard}`}
                            >
                                <div className={styles.errorHeader}>
                                    <XCircle size={24} />
                                    <h3>Analysis Failed</h3>
                                </div>
                                <div className={styles.crashLog}>
                                    <div className={styles.crashField}>
                                        <span className={styles.crashLabel}>Error Type:</span>
                                        <code>{error.error_type}</code>
                                    </div>
                                    <div className={styles.crashField}>
                                        <span className={styles.crashLabel}>Message:</span>
                                        <span>{error.error_message}</span>
                                    </div>
                                </div>
                            </motion.div>
                        )}

                        {result && !isAnalyzing && (
                            <motion.div
                                key="result"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0 }}
                                className={styles.resultContainer}
                            >
                                {/* Summary Card */}
                                <div className={`${styles.card} ${styles.summaryCard}`}>
                                    <div className={styles.cardHeader}>
                                        <CheckCircle size={20} className={styles.successIcon} />
                                        <h3>Research Analysis Complete</h3>
                                        <span className={`badge badge-${result.confidence}`}>
                                            {result.confidence} confidence
                                        </span>
                                    </div>
                                    <p className={styles.summary}>{result.query_summary}</p>
                                </div>

                                {/* Key Concepts */}
                                <div className={styles.card}>
                                    <h4>Key Concepts</h4>
                                    <div className={styles.tagList}>
                                        {result.key_concepts.map((concept, i) => (
                                            <span key={i} className={styles.tag}>
                                                {concept}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                {/* Related Topics */}
                                <div className={styles.card}>
                                    <h4>
                                        <TrendingUp size={18} />
                                        Related Topics
                                    </h4>
                                    <div className={styles.topicList}>
                                        {result.related_topics.map((topic, i) => (
                                            <div key={i} className={styles.topicItem}>
                                                <div className={styles.topicHeader}>
                                                    <span className={styles.topicName}>{topic.topic}</span>
                                                    <span
                                                        className={styles.relevanceBadge}
                                                        style={{ color: getRelevanceColor(topic.relevance) }}
                                                    >
                                                        {topic.relevance}
                                                    </span>
                                                </div>
                                                <p className={styles.topicDesc}>{topic.description}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Research Gaps */}
                                <div className={`${styles.card} ${styles.gapsCard}`}>
                                    <h4>
                                        <Target size={18} />
                                        Research Gaps & Opportunities
                                    </h4>
                                    <div className={styles.gapList}>
                                        {result.research_gaps.map((gap, i) => (
                                            <div key={i} className={styles.gapItem}>
                                                <div className={styles.gapHeader}>
                                                    <span className={styles.gapTitle}>{gap.gap}</span>
                                                    <span
                                                        className={styles.difficultyBadge}
                                                        style={{
                                                            background: `${getDifficultyColor(gap.difficulty)}20`,
                                                            color: getDifficultyColor(gap.difficulty),
                                                        }}
                                                    >
                                                        {gap.difficulty} Difficulty
                                                    </span>
                                                </div>
                                                <p className={styles.opportunityText}>
                                                    <Lightbulb size={14} />
                                                    {gap.opportunity}
                                                </p>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Suggested Directions */}
                                <div className={styles.card}>
                                    <h4>
                                        <ChevronRight size={18} />
                                        Suggested Research Directions
                                    </h4>
                                    <div className={styles.directionList}>
                                        {result.suggested_directions.map((dir, i) => (
                                            <div key={i} className={styles.directionItem}>
                                                <div className={styles.directionHeader}>
                                                    <span className={styles.directionTitle}>{dir.direction}</span>
                                                    <span
                                                        className={styles.impactBadge}
                                                        style={{ color: getRelevanceColor(dir.potential_impact) }}
                                                    >
                                                        {dir.potential_impact} Impact
                                                    </span>
                                                </div>
                                                <p className={styles.rationaleText}>{dir.rationale}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Methodology Suggestions */}
                                <div className={styles.card}>
                                    <h4>
                                        <Beaker size={18} />
                                        Methodology Suggestions
                                    </h4>
                                    <ul className={styles.methodList}>
                                        {result.methodology_suggestions.map((method, i) => (
                                            <li key={i}>{method}</li>
                                        ))}
                                    </ul>
                                </div>

                                {/* Challenges */}
                                <div className={`${styles.card} ${styles.challengesCard}`}>
                                    <h4>
                                        <AlertTriangle size={18} />
                                        Potential Challenges
                                    </h4>
                                    <ul className={styles.challengeList}>
                                        {result.potential_challenges.map((challenge, i) => (
                                            <li key={i}>{challenge}</li>
                                        ))}
                                    </ul>
                                </div>

                                {/* Unknowns */}
                                <div className={`${styles.card} ${styles.unknownsCard}`}>
                                    <h4>
                                        <AlertTriangle size={16} />
                                        Limitations
                                    </h4>
                                    <ul>
                                        {result.unknowns.map((unknown, i) => (
                                            <li key={i}>{unknown}</li>
                                        ))}
                                    </ul>
                                </div>

                                {/* Disclaimer */}
                                <div className={`${styles.card} ${styles.disclaimerBox}`}>
                                    <AlertTriangle size={16} />
                                    <p>{result.scope_disclaimer}</p>
                                </div>
                            </motion.div>
                        )}

                        {!isAnalyzing && !result && !error && (
                            <motion.div
                                key="empty"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className={styles.emptyState}
                            >
                                <BookOpen size={64} className={styles.emptyIcon} />
                                <h3>Ready to Explore</h3>
                                <p>Enter a research topic to discover gaps, trends, and opportunities</p>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    );
}
