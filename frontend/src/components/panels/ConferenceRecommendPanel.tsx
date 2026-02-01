"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    GraduationCap,
    Search,
    ExternalLink,
    Star,
    Calendar,
    Users,
    FileText,
    AlertTriangle,
    RefreshCw,
    Tag,
} from "lucide-react";
import styles from "./ConferenceRecommendPanel.module.css";

interface ConferenceRecommendation {
    name: string;
    domain: string;
    categories: string[];
    submission_types: string[];
    submission_url: string;
    relevance_score: number;
    reasoning: string;
    tier: string | null;
    acceptance_rate: string | null;
}

interface RecommendResponse {
    success: boolean;
    recommendations: ConferenceRecommendation[];
    analysis_summary: string;
    domain_detected: string;
    keywords_used: string[];
    methodology_detected: string;
    target_audience: string;
    total_found: number;
    warnings: string[];
    error_message?: string;
    status?: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ConferenceRecommendPanel() {
    const [title, setTitle] = useState("");
    const [abstract, setAbstract] = useState("");
    const [keywords, setKeywords] = useState<string[]>([]);
    const [keywordInput, setKeywordInput] = useState("");
    const [methodologyType, setMethodologyType] = useState<string>("");
    const [targetAudience, setTargetAudience] = useState<string>("");
    const [maxRecommendations, setMaxRecommendations] = useState(5);

    const [recommendations, setRecommendations] = useState<ConferenceRecommendation[]>([]);
    const [analysisSummary, setAnalysisSummary] = useState("");
    const [domainDetected, setDomainDetected] = useState("");
    const [warnings, setWarnings] = useState<string[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const methodologyOptions = [
        { value: "", label: "Auto-detect" },
        { value: "theoretical", label: "Theoretical" },
        { value: "applied", label: "Applied" },
        { value: "experimental", label: "Experimental" },
        { value: "mixed", label: "Mixed" },
    ];

    const audienceOptions = [
        { value: "", label: "Auto-detect" },
        { value: "academic", label: "Academic" },
        { value: "industry", label: "Industry" },
        { value: "hybrid", label: "Hybrid" },
    ];

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

    const handleRecommend = async () => {
        if (!title.trim() || !abstract.trim() || keywords.length === 0) {
            setError("Please provide title, abstract, and at least one keyword.");
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            const response = await fetch(`${API_URL}/api/draft-conference/recommend`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    title,
                    abstract,
                    keywords,
                    methodology_type: methodologyType || null,
                    target_audience: targetAudience || null,
                    max_recommendations: maxRecommendations,
                }),
            });

            // Check for HTTP errors first
            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                if (errorData?.detail) {
                    // Handle validation errors (422)
                    if (Array.isArray(errorData.detail)) {
                        const messages = errorData.detail.map((d: any) => d.msg || d.message || JSON.stringify(d)).join(", ");
                        setError(`Validation error: ${messages}`);
                    } else {
                        setError(typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail));
                    }
                } else {
                    setError(`Request failed with status ${response.status}`);
                }
                return;
            }

            const data: RecommendResponse = await response.json();

            if (!data.success || data.status === "CRASH" || data.error_message) {
                setError(data.error_message || "Recommendation failed");
                return;
            }

            setRecommendations(data.recommendations);
            setAnalysisSummary(data.analysis_summary);
            setDomainDetected(data.domain_detected);
            setWarnings(data.warnings || []);
        } catch (err) {
            setError("Failed to connect to the recommendation service. Please ensure the backend is running.");
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    const getTierColor = (tier: string | null) => {
        switch (tier) {
            case "A*":
                return styles.tierAStar;
            case "A":
                return styles.tierA;
            case "B":
                return styles.tierB;
            default:
                return styles.tierDefault;
        }
    };

    return (
        <div className={styles.panel}>
            <div className={styles.header}>
                <div className={styles.titleRow}>
                    <GraduationCap size={28} className={styles.icon} />
                    <div>
                        <h1>Conference Finder</h1>
                        <p>Find the perfect conferences for your research</p>
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

                {/* Options Section */}
                <div className={styles.section}>
                    <h3>Search Options</h3>
                    <div className={styles.optionsGrid}>
                        <div className={styles.inputGroup}>
                            <label>Methodology Type</label>
                            <select
                                value={methodologyType}
                                onChange={(e) => setMethodologyType(e.target.value)}
                                className={styles.select}
                            >
                                {methodologyOptions.map((opt) => (
                                    <option key={opt.value} value={opt.value}>
                                        {opt.label}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className={styles.inputGroup}>
                            <label>Target Audience</label>
                            <select
                                value={targetAudience}
                                onChange={(e) => setTargetAudience(e.target.value)}
                                className={styles.select}
                            >
                                {audienceOptions.map((opt) => (
                                    <option key={opt.value} value={opt.value}>
                                        {opt.label}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className={styles.inputGroup}>
                            <label>Max Recommendations</label>
                            <select
                                value={maxRecommendations}
                                onChange={(e) => setMaxRecommendations(Number(e.target.value))}
                                className={styles.select}
                            >
                                {[3, 5, 7, 10].map((n) => (
                                    <option key={n} value={n}>
                                        {n} conferences
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>
                </div>

                {/* Action Button */}
                <button
                    className={styles.searchBtn}
                    onClick={handleRecommend}
                    disabled={isLoading || !title.trim() || !abstract.trim() || keywords.length === 0}
                >
                    {isLoading ? (
                        <>
                            <RefreshCw size={20} className={styles.spin} />
                            Finding Conferences...
                        </>
                    ) : (
                        <>
                            <Search size={20} />
                            Find Conferences
                        </>
                    )}
                </button>

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

                {/* Results Section */}
                <AnimatePresence>
                    {recommendations.length > 0 && (
                        <motion.div
                            className={styles.results}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                        >
                            <div className={styles.resultHeader}>
                                <h3>Recommended Conferences</h3>
                                <span className={styles.domainBadge}>
                                    <Tag size={14} />
                                    {domainDetected.replace(/_/g, " ")}
                                </span>
                            </div>

                            <p className={styles.summary}>{analysisSummary}</p>

                            <div className={styles.conferenceGrid}>
                                {recommendations.map((conf, idx) => (
                                    <motion.div
                                        key={idx}
                                        className={styles.conferenceCard}
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: idx * 0.1 }}
                                    >
                                        <div className={styles.cardHeader}>
                                            <div className={styles.cardTitle}>
                                                <h4>{conf.name}</h4>
                                                {conf.tier && (
                                                    <span className={`${styles.tier} ${getTierColor(conf.tier)}`}>
                                                        {conf.tier}
                                                    </span>
                                                )}
                                            </div>
                                            <div className={styles.relevanceScore}>
                                                <Star size={14} />
                                                <span>{(conf.relevance_score * 100).toFixed(0)}%</span>
                                            </div>
                                        </div>

                                        <p className={styles.domain}>{conf.domain}</p>

                                        <div className={styles.categories}>
                                            {conf.categories.slice(0, 3).map((cat) => (
                                                <span key={cat} className={styles.category}>
                                                    {cat}
                                                </span>
                                            ))}
                                        </div>

                                        <div className={styles.metadata}>
                                            <div className={styles.metaItem}>
                                                <FileText size={14} />
                                                <span>{conf.submission_types.join(", ")}</span>
                                            </div>
                                            {conf.acceptance_rate && (
                                                <div className={styles.metaItem}>
                                                    <Users size={14} />
                                                    <span>Acceptance: {conf.acceptance_rate}</span>
                                                </div>
                                            )}
                                        </div>

                                        <p className={styles.reasoning}>{conf.reasoning}</p>

                                        <a
                                            href={conf.submission_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className={styles.applyBtn}
                                        >
                                            <span>Visit Conference</span>
                                            <ExternalLink size={14} />
                                        </a>
                                    </motion.div>
                                ))}
                            </div>

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
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* Notice */}
            <div className={styles.notice}>
                <AlertTriangle size={16} />
                <span>
                    These are suggestions only. Always verify deadlines and requirements on official conference websites.
                    This system does not auto-submit on your behalf.
                </span>
            </div>
        </div>
    );
}
