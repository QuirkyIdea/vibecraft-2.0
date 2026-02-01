"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Microscope,
    Search,
    ExternalLink,
    BarChart3,
    BookOpen,
    AlertTriangle,
    RefreshCw,
    ChevronDown,
    ChevronUp,
    Award,
    Lightbulb,
} from "lucide-react";
import styles from "./SimilarityScanPanel.module.css";

interface SimilarPaper {
    paper_id: string;
    title: string;
    authors: string;
    year: number;
    abstract: string;
    similarity_score: number;
    semantic_overlap: number;
    methodological_proximity: number;
    url: string | null;
}

interface UniqueContribution {
    category: string;
    description: string;
    supporting_evidence: string;
    existing_gaps: string[];
    confidence: number;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function SimilarityScanPanel() {
    const [title, setTitle] = useState("");
    const [abstract, setAbstract] = useState("");
    const [keywords, setKeywords] = useState<string[]>([]);
    const [keywordInput, setKeywordInput] = useState("");

    const [similarPapers, setSimilarPapers] = useState<SimilarPaper[]>([]);
    const [selectedPaper, setSelectedPaper] = useState<SimilarPaper | null>(null);
    const [uniqueContributions, setUniqueContributions] = useState<UniqueContribution[]>([]);
    const [noveltyAssessment, setNoveltyAssessment] = useState("");
    const [expandedPaper, setExpandedPaper] = useState<string | null>(null);

    const [isLoading, setIsLoading] = useState(false);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [warnings, setWarnings] = useState<string[]>([]);
    const [scanStats, setScanStats] = useState<{
        highest: number;
        avg: number;
        total: number;
    } | null>(null);

    const addKeyword = () => {
        if (keywordInput.trim() && !keywords.includes(keywordInput.trim())) {
            setKeywords([...keywords, keywordInput.trim()]);
            setKeywordInput("");
        }
    };

    const removeKeyword = (kw: string) => {
        setKeywords(keywords.filter((k) => k !== kw));
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === "Enter") {
            e.preventDefault();
            addKeyword();
        }
    };

    const handleScan = async () => {
        if (!title.trim() || !abstract.trim() || keywords.length === 0) {
            setError("Please provide title, abstract, and at least one keyword.");
            return;
        }

        setIsLoading(true);
        setError(null);
        setSimilarPapers([]);
        setUniqueContributions([]);

        try {
            const response = await fetch(`${API_URL}/api/analysis/similarity-scan`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    title,
                    abstract,
                    keywords,
                    max_results: 10,
                }),
            });

            const data = await response.json();

            if (data.status === "CRASH" || data.error_message) {
                setError(data.error_message || "Similarity scan failed");
                return;
            }

            setSimilarPapers(data.similar_papers);
            setScanStats({
                highest: data.highest_similarity,
                avg: data.avg_similarity,
                total: data.total_scanned,
            });
            setWarnings(data.warnings || []);
        } catch (err) {
            setError("Failed to connect to the similarity scan service.");
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleIdentifyUnique = async () => {
        if (similarPapers.length === 0) {
            setError("Please run a similarity scan first.");
            return;
        }

        setIsAnalyzing(true);
        setError(null);

        try {
            const response = await fetch(`${API_URL}/api/analysis/unique-contributions`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_title: title,
                    user_abstract: abstract,
                    similar_papers: similarPapers,
                }),
            });

            const data = await response.json();

            if (data.status === "CRASH" || data.error_message) {
                setError(data.error_message || "Unique contribution identification failed");
                return;
            }

            setUniqueContributions(data.unique_contributions);
            setNoveltyAssessment(data.overall_novelty_assessment);
        } catch (err) {
            setError("Failed to identify unique contributions.");
            console.error(err);
        } finally {
            setIsAnalyzing(false);
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 0.7) return styles.scoreHigh;
        if (score >= 0.4) return styles.scoreMedium;
        return styles.scoreLow;
    };

    return (
        <div className={styles.panel}>
            <div className={styles.header}>
                <div className={styles.titleRow}>
                    <Microscope size={28} className={styles.icon} />
                    <div>
                        <h1>Similarity Scan</h1>
                        <p>Scan scholarly literature and identify unique contributions</p>
                    </div>
                </div>
            </div>

            <div className={styles.content}>
                {/* Input Section */}
                <div className={styles.section}>
                    <h3>Research Details</h3>

                    <div className={styles.inputGroup}>
                        <label>Research Title</label>
                        <input
                            type="text"
                            className={styles.input}
                            placeholder="Enter your research title..."
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                        />
                    </div>

                    <div className={styles.inputGroup}>
                        <label>Abstract</label>
                        <textarea
                            className={styles.textArea}
                            placeholder="Paste your research abstract..."
                            value={abstract}
                            onChange={(e) => setAbstract(e.target.value)}
                            rows={6}
                        />
                    </div>

                    <div className={styles.inputGroup}>
                        <label>Keywords</label>
                        <div className={styles.keywordInput}>
                            <input
                                type="text"
                                placeholder="Add keyword and press Enter..."
                                value={keywordInput}
                                onChange={(e) => setKeywordInput(e.target.value)}
                                onKeyDown={handleKeyPress}
                            />
                            <button onClick={addKeyword} className={styles.addBtn}>
                                Add
                            </button>
                        </div>
                        {keywords.length > 0 && (
                            <div className={styles.keywordTags}>
                                {keywords.map((kw) => (
                                    <span key={kw} className={styles.keywordTag}>
                                        {kw}
                                        <button onClick={() => removeKeyword(kw)}>×</button>
                                    </span>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Action Buttons */}
                <div className={styles.actions}>
                    <button
                        className={styles.scanBtn}
                        onClick={handleScan}
                        disabled={isLoading || !title.trim() || !abstract.trim() || keywords.length === 0}
                    >
                        {isLoading ? (
                            <>
                                <RefreshCw size={20} className={styles.spin} />
                                Scanning Literature...
                            </>
                        ) : (
                            <>
                                <Search size={20} />
                                Scan Similar Papers
                            </>
                        )}
                    </button>

                    {similarPapers.length > 0 && (
                        <button
                            className={styles.analyzeBtn}
                            onClick={handleIdentifyUnique}
                            disabled={isAnalyzing}
                        >
                            {isAnalyzing ? (
                                <>
                                    <RefreshCw size={20} className={styles.spin} />
                                    Analyzing...
                                </>
                            ) : (
                                <>
                                    <Lightbulb size={20} />
                                    Identify Unique Contributions
                                </>
                            )}
                        </button>
                    )}
                </div>

                {/* Error Display */}
                {error && (
                    <motion.div
                        className={styles.error}
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                    >
                        <AlertTriangle size={20} />
                        <span>{error}</span>
                    </motion.div>
                )}

                {/* Scan Stats */}
                <AnimatePresence>
                    {scanStats && (
                        <motion.div
                            className={styles.stats}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                        >
                            <div className={styles.stat}>
                                <BarChart3 size={18} />
                                <div>
                                    <span className={styles.statValue}>
                                        {(scanStats.highest * 100).toFixed(0)}%
                                    </span>
                                    <span className={styles.statLabel}>Highest Similarity</span>
                                </div>
                            </div>
                            <div className={styles.stat}>
                                <BarChart3 size={18} />
                                <div>
                                    <span className={styles.statValue}>
                                        {(scanStats.avg * 100).toFixed(0)}%
                                    </span>
                                    <span className={styles.statLabel}>Average Similarity</span>
                                </div>
                            </div>
                            <div className={styles.stat}>
                                <BookOpen size={18} />
                                <div>
                                    <span className={styles.statValue}>{scanStats.total}</span>
                                    <span className={styles.statLabel}>Papers Found</span>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Similar Papers */}
                <AnimatePresence>
                    {similarPapers.length > 0 && (
                        <motion.div
                            className={styles.results}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                        >
                            <h3>Similar Papers</h3>
                            <div className={styles.papersList}>
                                {similarPapers.map((paper, idx) => (
                                    <motion.div
                                        key={paper.paper_id}
                                        className={styles.paperCard}
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: idx * 0.05 }}
                                    >
                                        <div className={styles.paperHeader}>
                                            <div className={styles.paperInfo}>
                                                <h4>{paper.title}</h4>
                                                <p className={styles.authors}>
                                                    {paper.authors} • {paper.year}
                                                </p>
                                            </div>
                                            <div className={`${styles.score} ${getScoreColor(paper.similarity_score)}`}>
                                                {(paper.similarity_score * 100).toFixed(0)}%
                                            </div>
                                        </div>

                                        <div className={styles.scoreBreakdown}>
                                            <div className={styles.scoreItem}>
                                                <span>Semantic Overlap</span>
                                                <div className={styles.scoreBar}>
                                                    <div
                                                        className={styles.scoreBarFill}
                                                        style={{ width: `${paper.semantic_overlap * 100}%` }}
                                                    />
                                                </div>
                                            </div>
                                            <div className={styles.scoreItem}>
                                                <span>Methodological Proximity</span>
                                                <div className={styles.scoreBar}>
                                                    <div
                                                        className={styles.scoreBarFill}
                                                        style={{ width: `${paper.methodological_proximity * 100}%` }}
                                                    />
                                                </div>
                                            </div>
                                        </div>

                                        <button
                                            className={styles.expandBtn}
                                            onClick={() =>
                                                setExpandedPaper(
                                                    expandedPaper === paper.paper_id ? null : paper.paper_id
                                                )
                                            }
                                        >
                                            {expandedPaper === paper.paper_id ? (
                                                <>
                                                    <ChevronUp size={16} /> Hide Abstract
                                                </>
                                            ) : (
                                                <>
                                                    <ChevronDown size={16} /> Show Abstract
                                                </>
                                            )}
                                        </button>

                                        <AnimatePresence>
                                            {expandedPaper === paper.paper_id && (
                                                <motion.div
                                                    className={styles.abstract}
                                                    initial={{ height: 0, opacity: 0 }}
                                                    animate={{ height: "auto", opacity: 1 }}
                                                    exit={{ height: 0, opacity: 0 }}
                                                >
                                                    <p>{paper.abstract}</p>
                                                    {paper.url && (
                                                        <a
                                                            href={paper.url}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className={styles.paperLink}
                                                        >
                                                            <ExternalLink size={14} /> View Paper
                                                        </a>
                                                    )}
                                                </motion.div>
                                            )}
                                        </AnimatePresence>
                                    </motion.div>
                                ))}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Unique Contributions */}
                <AnimatePresence>
                    {uniqueContributions.length > 0 && (
                        <motion.div
                            className={styles.uniqueSection}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                        >
                            <div className={styles.uniqueHeader}>
                                <Award size={24} className={styles.uniqueIcon} />
                                <div>
                                    <h3>Your Unique Contributions</h3>
                                    <p>{noveltyAssessment}</p>
                                </div>
                            </div>

                            <div className={styles.contributionsList}>
                                {uniqueContributions.map((contrib, idx) => (
                                    <motion.div
                                        key={idx}
                                        className={styles.contributionCard}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: idx * 0.1 }}
                                    >
                                        <div className={styles.contributionHeader}>
                                            <span className={styles.category}>
                                                {contrib.category.replace(/_/g, " ")}
                                            </span>
                                            <span className={styles.confidence}>
                                                Confidence: {(contrib.confidence * 100).toFixed(0)}%
                                            </span>
                                        </div>
                                        <p className={styles.description}>{contrib.description}</p>
                                        <div className={styles.evidence}>
                                            <strong>Supporting Evidence:</strong>
                                            <p>{contrib.supporting_evidence}</p>
                                        </div>
                                        {contrib.existing_gaps.length > 0 && (
                                            <div className={styles.gaps}>
                                                <strong>Gaps in Existing Work:</strong>
                                                <ul>
                                                    {contrib.existing_gaps.map((gap, i) => (
                                                        <li key={i}>{gap}</li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                    </motion.div>
                                ))}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Warnings */}
                {warnings.length > 0 && (
                    <div className={styles.warnings}>
                        {warnings.map((warning, idx) => (
                            <div key={idx} className={styles.warning}>
                                <AlertTriangle size={14} />
                                <span>{warning}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Notice */}
            <div className={styles.notice}>
                <AlertTriangle size={16} />
                <span>
                    This is NOT a patentability assessment. Similarity scores are probabilistic estimates.
                    Professional literature review is recommended.
                </span>
            </div>
        </div>
    );
}
