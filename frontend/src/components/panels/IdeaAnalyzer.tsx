"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Lightbulb,
    Send,
    Loader2,
    AlertTriangle,
    CheckCircle,
    XCircle,
    Info,
} from "lucide-react";
import { useStats } from "@/context/StatsContext";
import PDFUpload from "@/components/PDFUpload";
import styles from "./IdeaAnalyzer.module.css";

interface NoveltyScore {
    overall_score: number;
    semantic_uniqueness: number;
    domain_coverage: number;
    prior_art_risk: number;
}

interface AnalysisResult {
    idea_summary: string;
    key_concepts: string[];
    novelty_indicators: NoveltyScore;
    potential_overlaps: string[];
    recommended_searches: string[];
    evidence_references: { evidence_id: string; source: string }[];
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

export default function IdeaAnalyzer() {
    const { recordIdeaAnalysis } = useStats();
    const [ideaText, setIdeaText] = useState("");
    const [domain, setDomain] = useState("");
    const [context, setContext] = useState("");
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [result, setResult] = useState<AnalysisResult | null>(null);
    const [error, setError] = useState<CrashLog | null>(null);

    const analyzeIdea = async () => {
        if (!ideaText.trim() || ideaText.length < 10) return;

        setIsAnalyzing(true);
        setResult(null);
        setError(null);

        try {
            const response = await fetch("http://localhost:8000/api/analysis/idea", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    idea_text: ideaText,
                    domain: domain || undefined,
                    context: context || undefined,
                }),
            });

            const data = await response.json();

            if (data.status === "CRASH") {
                setError(data as CrashLog);
            } else {
                const analysisResult = data as AnalysisResult;
                setResult(analysisResult);
                // Record stats
                const confidenceMap: Record<string, number> = {
                    low: 0.3,
                    medium: 0.6,
                    high: 0.9,
                };
                recordIdeaAnalysis(
                    ideaText,
                    confidenceMap[analysisResult.confidence] || 0.5
                );
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

    const getScoreColor = (score: number) => {
        if (score >= 0.7) return "var(--success)";
        if (score >= 0.4) return "var(--warning)";
        return "var(--error)";
    };

    const getRiskColor = (risk: number) => {
        if (risk >= 0.7) return "var(--error)";
        if (risk >= 0.4) return "var(--warning)";
        return "var(--success)";
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <div className={styles.headerIcon}>
                    <Lightbulb size={24} />
                </div>
                <div>
                    <h1>Idea Analyzer</h1>
                    <p>Analyze innovation ideas for novelty indicators and semantic uniqueness</p>
                </div>
            </div>

            <div className={styles.mainContent}>
                <div className={styles.inputSection}>
                    <div className={styles.card}>
                        <h3>Enter Your Idea</h3>

                        {/* PDF Upload */}
                        <div className={styles.inputGroup}>
                            <label className="label">Upload PDF (optional)</label>
                            <PDFUpload
                                onTextExtracted={(text) => {
                                    setIdeaText(prev => prev + (prev ? "\n\n" : "") + text);
                                }}
                                compact
                            />
                        </div>

                        <div className={styles.divider}>
                            <span>or enter text manually</span>
                        </div>

                        <div className={styles.inputGroup}>
                            <label className="label">Idea Description *</label>
                            <textarea
                                className={`input ${styles.ideaInput}`}
                                placeholder="Describe your innovation idea in detail. What problem does it solve? What makes it unique?"
                                value={ideaText}
                                onChange={(e) => setIdeaText(e.target.value)}
                            />
                            <span className={styles.charCount}>{ideaText.length} characters</span>
                        </div>

                        <div className={styles.inputRow}>
                            <div className={styles.inputGroup}>
                                <label className="label">Technology Domain</label>
                                <input
                                    className="input"
                                    placeholder="e.g., Machine Learning, IoT, Biotech"
                                    value={domain}
                                    onChange={(e) => setDomain(e.target.value)}
                                />
                            </div>
                            <div className={styles.inputGroup}>
                                <label className="label">Additional Context</label>
                                <input
                                    className="input"
                                    placeholder="Any relevant background information"
                                    value={context}
                                    onChange={(e) => setContext(e.target.value)}
                                />
                            </div>
                        </div>

                        <button
                            className={`btn btn-primary ${styles.analyzeBtn}`}
                            onClick={analyzeIdea}
                            disabled={isAnalyzing || ideaText.length < 10}
                        >
                            {isAnalyzing ? (
                                <>
                                    <Loader2 size={18} className={styles.spinner} />
                                    Analyzing...
                                </>
                            ) : (
                                <>
                                    <Send size={18} />
                                    Analyze Idea
                                </>
                            )}
                        </button>

                        <div className={styles.disclaimer}>
                            <Info size={14} />
                            <span>
                                This analysis provides probabilistic indicators only. It does not
                                determine patentability or commercial viability.
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
                                <div className={styles.loadingOrb}>
                                    <motion.div
                                        className={styles.orbInner}
                                        animate={{
                                            scale: [1, 1.2, 1],
                                            opacity: [0.5, 1, 0.5],
                                        }}
                                        transition={{ duration: 1.5, repeat: Infinity }}
                                    />
                                </div>
                                <p>ANTIGRAVITY processing...</p>
                                <span className={styles.loadingSubtext}>
                                    Extracting concepts and analyzing novelty signals
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
                                    <div className={styles.crashField}>
                                        <span className={styles.crashLabel}>Failed Stage:</span>
                                        <code>{error.failed_stage}</code>
                                    </div>
                                    <div className={styles.crashField}>
                                        <span className={styles.crashLabel}>Recommended:</span>
                                        <span>{error.recommended_action}</span>
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
                                <div className={`${styles.card} ${styles.summaryCard}`}>
                                    <div className={styles.cardHeader}>
                                        <CheckCircle size={20} className={styles.successIcon} />
                                        <h3>Analysis Complete</h3>
                                        <span className={`badge badge-${result.confidence}`}>
                                            {result.confidence} confidence
                                        </span>
                                    </div>
                                    <p className={styles.summary}>{result.idea_summary}</p>
                                </div>

                                <div className={styles.scoresGrid}>
                                    <div className={styles.scoreCard}>
                                        <span className={styles.scoreLabel}>Overall Novelty</span>
                                        <div className={styles.scoreValue}>
                                            <span
                                                style={{
                                                    color: getScoreColor(result.novelty_indicators.overall_score),
                                                }}
                                            >
                                                {(result.novelty_indicators.overall_score * 100).toFixed(0)}%
                                            </span>
                                        </div>
                                        <div className="progress-bar">
                                            <div
                                                className="progress-fill"
                                                style={{
                                                    width: `${result.novelty_indicators.overall_score * 100}%`,
                                                    background: getScoreColor(
                                                        result.novelty_indicators.overall_score
                                                    ),
                                                }}
                                            />
                                        </div>
                                    </div>

                                    <div className={styles.scoreCard}>
                                        <span className={styles.scoreLabel}>Semantic Uniqueness</span>
                                        <div className={styles.scoreValue}>
                                            <span
                                                style={{
                                                    color: getScoreColor(
                                                        result.novelty_indicators.semantic_uniqueness
                                                    ),
                                                }}
                                            >
                                                {(result.novelty_indicators.semantic_uniqueness * 100).toFixed(
                                                    0
                                                )}
                                                %
                                            </span>
                                        </div>
                                        <div className="progress-bar">
                                            <div
                                                className="progress-fill"
                                                style={{
                                                    width: `${result.novelty_indicators.semantic_uniqueness * 100}%`,
                                                    background: getScoreColor(
                                                        result.novelty_indicators.semantic_uniqueness
                                                    ),
                                                }}
                                            />
                                        </div>
                                    </div>

                                    <div className={styles.scoreCard}>
                                        <span className={styles.scoreLabel}>Domain Coverage</span>
                                        <div className={styles.scoreValue}>
                                            <span
                                                style={{
                                                    color: getScoreColor(
                                                        result.novelty_indicators.domain_coverage
                                                    ),
                                                }}
                                            >
                                                {(result.novelty_indicators.domain_coverage * 100).toFixed(0)}%
                                            </span>
                                        </div>
                                        <div className="progress-bar">
                                            <div
                                                className="progress-fill"
                                                style={{
                                                    width: `${result.novelty_indicators.domain_coverage * 100}%`,
                                                    background: getScoreColor(
                                                        result.novelty_indicators.domain_coverage
                                                    ),
                                                }}
                                            />
                                        </div>
                                    </div>

                                    <div className={styles.scoreCard}>
                                        <span className={styles.scoreLabel}>Prior Art Risk</span>
                                        <div className={styles.scoreValue}>
                                            <span
                                                style={{
                                                    color: getRiskColor(
                                                        result.novelty_indicators.prior_art_risk
                                                    ),
                                                }}
                                            >
                                                {(result.novelty_indicators.prior_art_risk * 100).toFixed(0)}%
                                            </span>
                                        </div>
                                        <div className="progress-bar">
                                            <div
                                                className="progress-fill"
                                                style={{
                                                    width: `${result.novelty_indicators.prior_art_risk * 100}%`,
                                                    background: getRiskColor(
                                                        result.novelty_indicators.prior_art_risk
                                                    ),
                                                }}
                                            />
                                        </div>
                                    </div>
                                </div>

                                <div className={styles.detailsGrid}>
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

                                    <div className={styles.card}>
                                        <h4>Potential Overlaps</h4>
                                        <ul className={styles.overlapList}>
                                            {result.potential_overlaps.map((overlap, i) => (
                                                <li key={i}>{overlap}</li>
                                            ))}
                                        </ul>
                                    </div>

                                    <div className={styles.card}>
                                        <h4>Recommended Searches</h4>
                                        <ul className={styles.searchList}>
                                            {result.recommended_searches.map((search, i) => (
                                                <li key={i}>
                                                    <code>{search}</code>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>

                                    <div className={`${styles.card} ${styles.unknownsCard}`}>
                                        <h4>
                                            <AlertTriangle size={16} />
                                            Unknowns
                                        </h4>
                                        <ul>
                                            {result.unknowns.map((unknown, i) => (
                                                <li key={i}>{unknown}</li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>

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
                                <Lightbulb size={64} className={styles.emptyIcon} />
                                <h3>Ready to Analyze</h3>
                                <p>Enter your innovation idea to receive novelty indicators and analysis</p>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    );
}
