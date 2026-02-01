"use client";

import React, { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import styles from "./AntigravityPanel.module.css";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Types for ANTIGRAVITY responses
interface ConceptResult {
    term: string;
    category: string;
    frequency: number;
    weight: number;
    context?: string;
}

interface PriorArtMatch {
    title: string;
    source: string;
    similarity: string;
    similarity_score: number;
    overlap_description: string;
    overlapping_concepts: string[];
    differentiating_aspects: string[];
    evidence: string;
}

interface AnalysisResults {
    concepts?: {
        success: boolean;
        differentiating_terms: string[];
        common_terms: string[];
        summary: Record<string, number>;
    };
    novelty?: {
        success: boolean;
        risk: string;
        risk_score: number;
        confidence: string;
        novel_aspects: string[];
        overlapping_aspects: string[];
        recommendations: string[];
    };
    summary?: {
        success: boolean;
        existing_work: string;
        user_contribution: string;
        differentiation: string;
        key_innovations: string[];
    };
    refinement?: {
        success: boolean;
        refined_text: string;
        change_count: number;
        warnings: string[];
    };
}

type ActiveTab = "upload" | "concepts" | "prior-art" | "summary" | "refine" | "full";

export default function AntigravityPanel() {
    const [activeTab, setActiveTab] = useState<ActiveTab>("upload");
    const [inputText, setInputText] = useState("");
    const [title, setTitle] = useState("");
    const [projectType, setProjectType] = useState<"research" | "patent">("research");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Results state
    const [documentResult, setDocumentResult] = useState<any>(null);
    const [conceptsResult, setConceptsResult] = useState<any>(null);
    const [priorArtResult, setPriorArtResult] = useState<any>(null);
    const [summaryResult, setSummaryResult] = useState<any>(null);
    const [refinementResult, setRefinementResult] = useState<any>(null);
    const [fullAnalysisResult, setFullAnalysisResult] = useState<AnalysisResults | null>(null);

    // File upload handler
    const handleFileUpload = useCallback(async (file: File) => {
        setIsLoading(true);
        setError(null);

        try {
            const formData = new FormData();
            formData.append("file", file);

            const response = await fetch(`${API_URL}/api/antigravity/document/upload`, {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (data.success) {
                setDocumentResult(data);
                setInputText(data.text);
            } else {
                setError(data.error_message || "Failed to process document");
            }
        } catch (err) {
            setError("Failed to upload document");
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Drag and drop handlers
    const [isDragging, setIsDragging] = useState(false);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);

        const file = e.dataTransfer.files[0];
        if (file) {
            handleFileUpload(file);
        }
    };

    // API call handlers
    const extractConcepts = async () => {
        setIsLoading(true);
        setError(null);

        try {
            console.log("Extracting concepts for:", inputText.substring(0, 100));
            const response = await fetch(`${API_URL}/api/antigravity/concepts/extract`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    text: inputText,
                    title: title,
                    project_type: projectType,
                }),
            });

            const data = await response.json();
            console.log("Concepts result:", data);
            setConceptsResult(data);
            if (!data.success) {
                setError(data.error || "Failed to extract concepts");
            }
        } catch (err) {
            console.error("Concept extraction error:", err);
            setError("Failed to extract concepts. Please check your connection.");
        } finally {
            setIsLoading(false);
        }
    };

    const comparePriorArt = async () => {
        setIsLoading(true);
        setError(null);

        try {
            console.log("Comparing prior art for:", title || "Untitled");
            const response = await fetch(`${API_URL}/api/antigravity/prior-art/compare`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    text: inputText,
                    title: title,
                    project_type: projectType,
                }),
            });

            const data = await response.json();
            console.log("Prior art result:", data);
            setPriorArtResult(data);
            if (!data.success) {
                setError(data.error || "Prior art comparison could not be completed");
            }
        } catch (err) {
            console.error("Prior art comparison error:", err);
            setError("Failed to compare with prior art. Please check your connection.");
        } finally {
            setIsLoading(false);
        }
    };

    const generateSummary = async () => {
        setIsLoading(true);
        setError(null);

        try {
            console.log("Generating summary for:", title || "Untitled");
            const response = await fetch(`${API_URL}/api/antigravity/summary/generate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    text: inputText,
                    title: title,
                    project_type: projectType,
                }),
            });

            const data = await response.json();
            console.log("Summary result:", data);
            setSummaryResult(data);
            if (!data.success) {
                setError(data.error || "Summary generation could not be completed");
            }
        } catch (err) {
            console.error("Summary generation error:", err);
            setError("Failed to generate summary. Please check your connection.");
        } finally {
            setIsLoading(false);
        }
    };

    const refineDraft = async () => {
        setIsLoading(true);
        setError(null);

        try {
            console.log("Refining draft...");
            const response = await fetch(`${API_URL}/api/antigravity/refine/draft`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    text: inputText,
                    change_level: "moderate",
                }),
            });

            const data = await response.json();
            console.log("Refinement result:", data);
            setRefinementResult(data);
            if (!data.success) {
                setError(data.error || "Draft refinement could not be completed");
            }
        } catch (err) {
            console.error("Draft refinement error:", err);
            setError("Failed to refine draft. Please check your connection.");
        } finally {
            setIsLoading(false);
        }
    };

    const runFullAnalysis = async () => {
        setIsLoading(true);
        setError(null);

        try {
            console.log("Running full analysis for:", title || "Untitled");
            const response = await fetch(`${API_URL}/api/antigravity/analyze/full`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    text: inputText,
                    title: title,
                    project_type: projectType,
                    include_refinement: false,
                }),
            });

            const data = await response.json();
            console.log("Full analysis result:", data);
            setFullAnalysisResult(data);
            if (!data.success) {
                setError("Full analysis could not be completed");
            }
        } catch (err) {
            console.error("Full analysis error:", err);
            setError("Failed to run full analysis. Please check your connection.");
        } finally {
            setIsLoading(false);
        }
    };

    const getRiskColor = (risk: string) => {
        switch (risk?.toLowerCase()) {
            case "green": return "#22c55e";
            case "yellow": return "#eab308";
            case "red": return "#ef4444";
            default: return "#6b7280";
        }
    };

    const renderUploadTab = () => (
        <div className={styles.uploadSection}>
            <h3 className={styles.sectionTitle}>Document Input</h3>

            {/* Drag and Drop Zone */}
            <div
                className={`${styles.dropZone} ${isDragging ? styles.dragging : ""}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
            >
                <div className={styles.dropIcon}>
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                        <polyline points="17,8 12,3 7,8" />
                        <line x1="12" y1="3" x2="12" y2="15" />
                    </svg>
                </div>
                <p>Drag & drop PDF, DOCX, or TXT file here</p>
                <span>or</span>
                <label className={styles.fileInputLabel}>
                    Browse Files
                    <input
                        type="file"
                        accept=".pdf,.docx,.doc,.txt"
                        onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
                        hidden
                    />
                </label>
            </div>

            {/* Document Info */}
            {documentResult && (
                <div className={styles.docInfo}>
                    <span className={styles.docBadge}>Document Loaded</span>
                    <p>{documentResult.word_count} words | {documentResult.paragraph_count} paragraphs</p>
                </div>
            )}

            {/* Text Input */}
            <div className={styles.textInputSection}>
                <label>Or paste your text directly:</label>
                <textarea
                    className={styles.textArea}
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Paste your research idea, patent claim, or document text here..."
                    rows={10}
                />
            </div>

            {/* Metadata */}
            <div className={styles.metadataRow}>
                <div className={styles.inputGroup}>
                    <label>Title</label>
                    <input
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="Enter project title"
                        className={styles.textInput}
                    />
                </div>
                <div className={styles.inputGroup}>
                    <label>Project Type</label>
                    <select
                        value={projectType}
                        onChange={(e) => setProjectType(e.target.value as "research" | "patent")}
                        className={styles.selectInput}
                    >
                        <option value="research">Research</option>
                        <option value="patent">Patent</option>
                    </select>
                </div>
            </div>

            {inputText && (
                <button
                    className={styles.primaryBtn}
                    onClick={() => setActiveTab("full")}
                >
                    Proceed to Analysis
                </button>
            )}
        </div>
    );

    const renderConceptsTab = () => (
        <div className={styles.analysisSection}>
            <h3 className={styles.sectionTitle}>Concept Extraction</h3>
            <p className={styles.sectionDesc}>
                Extract key concepts, technical terms, and identify differentiating elements.
            </p>

            {!inputText && (
                <div className={styles.noInputNotice}>
                    Please enter text in the Input tab first before running analysis.
                    <button onClick={() => setActiveTab("upload")} className={styles.goToInputBtn}>
                        Go to Input
                    </button>
                </div>
            )}

            <button
                className={styles.analyzeBtn}
                onClick={extractConcepts}
                disabled={!inputText || isLoading}
            >
                {isLoading ? "Extracting..." : "Extract Concepts"}
            </button>

            {conceptsResult?.success && (
                <div className={styles.resultsGrid}>
                    <div className={styles.resultCard}>
                        <h4>Differentiating Terms</h4>
                        <p className={styles.cardDesc}>Potentially novel or unique concepts</p>
                        <div className={styles.tagList}>
                            {conceptsResult.differentiating_terms.map((term: string, i: number) => (
                                <span key={i} className={styles.tagDifferentiating}>{term}</span>
                            ))}
                        </div>
                    </div>

                    <div className={styles.resultCard}>
                        <h4>Common Domain Terms</h4>
                        <p className={styles.cardDesc}>Standard vocabulary in this field</p>
                        <div className={styles.tagList}>
                            {conceptsResult.common_terms.map((term: string, i: number) => (
                                <span key={i} className={styles.tagCommon}>{term}</span>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );

    const renderPriorArtTab = () => (
        <div className={styles.analysisSection}>
            <h3 className={styles.sectionTitle}>Prior Art Comparison</h3>
            <p className={styles.sectionDesc}>
                Compare your idea against existing research papers or patents using semantic similarity.
            </p>

            <button
                className={styles.analyzeBtn}
                onClick={comparePriorArt}
                disabled={!inputText || isLoading}
            >
                {isLoading ? "Comparing..." : "Compare with Prior Art"}
            </button>

            {priorArtResult?.success && (
                <div className={styles.priorArtResults}>
                    {/* Risk Indicator */}
                    <div
                        className={styles.riskIndicator}
                        style={{ borderColor: getRiskColor(priorArtResult.risk) }}
                    >
                        <div
                            className={styles.riskBadge}
                            style={{ backgroundColor: getRiskColor(priorArtResult.risk) }}
                        >
                            {priorArtResult.risk.toUpperCase()}
                        </div>
                        <div className={styles.riskDetails}>
                            <span>Overlap Risk: {Math.round(priorArtResult.risk_score * 100)}%</span>
                            <span>Confidence: {priorArtResult.confidence}</span>
                        </div>
                    </div>

                    {/* Novel Aspects */}
                    <div className={styles.resultCard}>
                        <h4>Novel Aspects</h4>
                        <ul className={styles.aspectList}>
                            {priorArtResult.novel_aspects.map((aspect: string, i: number) => (
                                <li key={i} className={styles.novelAspect}>{aspect}</li>
                            ))}
                        </ul>
                    </div>

                    {/* Overlapping Aspects */}
                    <div className={styles.resultCard}>
                        <h4>Overlapping Aspects</h4>
                        <ul className={styles.aspectList}>
                            {priorArtResult.overlapping_aspects.map((aspect: string, i: number) => (
                                <li key={i} className={styles.overlapAspect}>{aspect}</li>
                            ))}
                        </ul>
                    </div>

                    {/* Prior Art Matches */}
                    {priorArtResult.prior_art_matches?.length > 0 && (
                        <div className={styles.matchesSection}>
                            <h4>Related Prior Art</h4>
                            {priorArtResult.prior_art_matches.map((match: PriorArtMatch, i: number) => (
                                <div key={i} className={styles.matchCard}>
                                    <div className={styles.matchHeader}>
                                        <span className={styles.matchTitle}>{match.title}</span>
                                        <span
                                            className={styles.similarityBadge}
                                            style={{
                                                backgroundColor: match.similarity === "high" ? "#ef4444" :
                                                    match.similarity === "medium" ? "#eab308" : "#22c55e"
                                            }}
                                        >
                                            {Math.round(match.similarity_score * 100)}% similar
                                        </span>
                                    </div>
                                    <p className={styles.matchOverlap}>{match.overlap_description}</p>
                                    {match.differentiating_aspects.length > 0 && (
                                        <p className={styles.matchDiff}>
                                            <strong>Your differentiators:</strong> {match.differentiating_aspects.join(", ")}
                                        </p>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Recommendations */}
                    <div className={styles.recommendationsCard}>
                        <h4>Recommendations</h4>
                        <ul>
                            {priorArtResult.recommendations.map((rec: string, i: number) => (
                                <li key={i}>{rec}</li>
                            ))}
                        </ul>
                    </div>
                </div>
            )}
        </div>
    );

    const renderSummaryTab = () => (
        <div className={styles.analysisSection}>
            <h3 className={styles.sectionTitle}>Structured Summary</h3>
            <p className={styles.sectionDesc}>
                Generate an evidence-grounded summary separating existing work, your contribution, and uncertainties.
            </p>

            <button
                className={styles.analyzeBtn}
                onClick={generateSummary}
                disabled={!inputText || isLoading}
            >
                {isLoading ? "Generating..." : "Generate Summary"}
            </button>

            {summaryResult?.success && (
                <div className={styles.summaryResults}>
                    <div className={styles.summarySection}>
                        <h4>Existing Work</h4>
                        <p>{summaryResult.existing_work}</p>
                    </div>

                    <div className={styles.summarySection}>
                        <h4>Your Contribution</h4>
                        <p>{summaryResult.user_contribution}</p>
                    </div>

                    <div className={styles.summarySection}>
                        <h4>Differentiation</h4>
                        <p>{summaryResult.differentiation}</p>
                    </div>

                    <div className={styles.summarySection}>
                        <h4>Uncertainty</h4>
                        <p className={styles.uncertaintyText}>{summaryResult.uncertainty}</p>
                    </div>

                    {summaryResult.key_innovations?.length > 0 && (
                        <div className={styles.innovationsCard}>
                            <h4>Key Innovations</h4>
                            <ul>
                                {summaryResult.key_innovations.map((innovation: string, i: number) => (
                                    <li key={i}>{innovation}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}
        </div>
    );

    const renderRefineTab = () => (
        <div className={styles.analysisSection}>
            <h3 className={styles.sectionTitle}>Draft Refinement</h3>
            <p className={styles.sectionDesc}>
                Improve clarity, structure, and precision without adding new claims or fabricating content.
            </p>

            <button
                className={styles.analyzeBtn}
                onClick={refineDraft}
                disabled={!inputText || isLoading}
            >
                {isLoading ? "Refining..." : "Refine Draft"}
            </button>

            {refinementResult?.success && (
                <div className={styles.refinementResults}>
                    {refinementResult.warnings?.length > 0 && (
                        <div className={styles.warningsCard}>
                            <h4>Warnings</h4>
                            <ul>
                                {refinementResult.warnings.map((warning: string, i: number) => (
                                    <li key={i}>{warning}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    <div className={styles.refinedTextSection}>
                        <div className={styles.refinedHeader}>
                            <h4>Refined Draft</h4>
                            <span className={styles.changeBadge}>
                                {refinementResult.changes?.length || 0} changes made
                            </span>
                        </div>
                        <div className={styles.refinedText}>
                            {refinementResult.refined_text}
                        </div>
                        <button
                            className={styles.copyBtn}
                            onClick={() => navigator.clipboard.writeText(refinementResult.refined_text)}
                        >
                            Copy to Clipboard
                        </button>
                    </div>

                    {refinementResult.changes?.length > 0 && (
                        <div className={styles.changesSection}>
                            <h4>Changes Made</h4>
                            {refinementResult.changes.slice(0, 5).map((change: any, i: number) => (
                                <div key={i} className={styles.changeItem}>
                                    <span className={styles.changeType}>{change.type}</span>
                                    <div className={styles.changeDiff}>
                                        <div className={styles.changeOriginal}>{change.original}</div>
                                        <div className={styles.changeArrow}>→</div>
                                        <div className={styles.changeRefined}>{change.refined}</div>
                                    </div>
                                    <p className={styles.changeReason}>{change.reason}</p>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );

    const renderFullAnalysisTab = () => (
        <div className={styles.fullAnalysisSection}>
            <h3 className={styles.sectionTitle}>Full Analysis & Summarization</h3>
            <p className={styles.sectionDesc}>
                Run the complete analysis pipeline: concept extraction, prior art comparison,
                novelty assessment, summary generation, and optional draft refinement.
            </p>

            <button
                className={styles.primaryBtn}
                onClick={runFullAnalysis}
                disabled={!inputText || isLoading}
            >
                {isLoading ? "Running Full Analysis..." : "Run Full Analysis"}
            </button>

            {fullAnalysisResult && (
                <div className={styles.fullResultsContainer}>
                    {/* Concepts Summary */}
                    {fullAnalysisResult.concepts?.success && (
                        <div className={styles.fullResultCard}>
                            <h4>Concept Analysis</h4>
                            <div className={styles.miniTagList}>
                                <strong>Differentiating:</strong>
                                {fullAnalysisResult.concepts.differentiating_terms.slice(0, 5).map((t, i) => (
                                    <span key={i} className={styles.tagDifferentiating}>{t}</span>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Novelty Summary */}
                    {fullAnalysisResult.novelty?.success && (
                        <div className={styles.fullResultCard}>
                            <h4>Novelty Assessment</h4>
                            <div
                                className={styles.riskBadgeLarge}
                                style={{ backgroundColor: getRiskColor(fullAnalysisResult.novelty.risk) }}
                            >
                                {fullAnalysisResult.novelty.risk.toUpperCase()} RISK
                            </div>
                            <p>Score: {Math.round((1 - fullAnalysisResult.novelty.risk_score) * 100)}% Novel</p>
                            <p>Confidence: {fullAnalysisResult.novelty.confidence}</p>
                        </div>
                    )}

                    {/* Summary */}
                    {fullAnalysisResult.summary?.success && (
                        <div className={styles.fullResultCard}>
                            <h4>Key Insights</h4>
                            <div className={styles.insightItem}>
                                <strong>Your Contribution:</strong>
                                <p>{fullAnalysisResult.summary.user_contribution}</p>
                            </div>
                            <div className={styles.insightItem}>
                                <strong>Differentiation:</strong>
                                <p>{fullAnalysisResult.summary.differentiation}</p>
                            </div>
                        </div>
                    )}

                    {/* Recommendations */}
                    {fullAnalysisResult.novelty?.recommendations && (
                        <div className={styles.fullResultCard}>
                            <h4>Recommendations</h4>
                            <ul className={styles.recList}>
                                {fullAnalysisResult.novelty.recommendations.map((rec, i) => (
                                    <li key={i}>{rec}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}
        </div>
    );

    const tabs = [
        { id: "upload", label: "Input", icon: "📄" },
        { id: "concepts", label: "Concepts", icon: "🔍" },
        { id: "prior-art", label: "Prior Art", icon: "📚" },
        { id: "summary", label: "Summary", icon: "📝" },
        { id: "refine", label: "Refine", icon: "✨" },
        { id: "full", label: "Full Analysis", icon: "🚀" },
    ];

    return (
        <div className={styles.container}>
            <header className={styles.header}>
                <h1 className={styles.title}>Full Analysis & Summarization</h1>
                <p className={styles.subtitle}>Evidence-Locked Research & Patent Intelligence</p>
            </header>

            {error && (
                <div className={styles.errorBanner}>
                    <span>{error}</span>
                    <button onClick={() => setError(null)}>✕</button>
                </div>
            )}

            <nav className={styles.tabNav}>
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        className={`${styles.tabBtn} ${activeTab === tab.id ? styles.activeTab : ""}`}
                        onClick={() => setActiveTab(tab.id as ActiveTab)}
                    >
                        <span className={styles.tabIcon}>{tab.icon}</span>
                        <span>{tab.label}</span>
                    </button>
                ))}
            </nav>

            <main className={styles.content}>
                <AnimatePresence mode="wait">
                    <motion.div
                        key={activeTab}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.2 }}
                    >
                        {activeTab === "upload" && renderUploadTab()}
                        {activeTab === "concepts" && renderConceptsTab()}
                        {activeTab === "prior-art" && renderPriorArtTab()}
                        {activeTab === "summary" && renderSummaryTab()}
                        {activeTab === "refine" && renderRefineTab()}
                        {activeTab === "full" && renderFullAnalysisTab()}
                    </motion.div>
                </AnimatePresence>
            </main>

            {isLoading && (
                <div className={styles.loadingOverlay}>
                    <div className={styles.spinner}></div>
                    <p>Analyzing your content...</p>
                </div>
            )}
        </div>
    );
}
