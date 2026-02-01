"use client";

import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    FileEdit,
    Upload,
    Download,
    RefreshCw,
    CheckCircle,
    AlertTriangle,
    FileText,
    Sparkles,
    ChevronDown,
    ChevronUp,
    X,
} from "lucide-react";
import styles from "./DraftRefinementPanel.module.css";

interface RefinementChange {
    type: string;
    original: string;
    refined: string;
    reason: string;
    accepted?: boolean;
    id?: string;
}

interface RefineResponse {
    success: boolean;
    original_text: string;
    refined_text: string;
    changes: RefinementChange[];
    change_summary: Record<string, number>;
    word_count_original: number;
    word_count_refined: number;
    warnings: string[];
    diff_html?: string;
    error?: string;
    status?: string;
    error_message?: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function DraftRefinementPanel() {
    const [draftText, setDraftText] = useState("");
    const [refinedText, setRefinedText] = useState("");
    const [changes, setChanges] = useState<RefinementChange[]>([]);
    const [changeSummary, setChangeSummary] = useState<Record<string, number>>({});
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [uploadedFile, setUploadedFile] = useState<File | null>(null);
    const [showChanges, setShowChanges] = useState(false);
    const [focusAreas, setFocusAreas] = useState<string[]>(["clarity", "grammar", "flow"]);
    const [changeLevel, setChangeLevel] = useState<"light" | "moderate" | "thorough">("moderate");
    const [wordCounts, setWordCounts] = useState({ original: 0, refined: 0 });
    const [warnings, setWarnings] = useState<string[]>([]);
    const [viewMode, setViewMode] = useState<"split" | "refined">("refined");
    const [exportFormat, setExportFormat] = useState<"txt" | "docx" | "pdf">("txt");
    const [showExportMenu, setShowExportMenu] = useState(false);

    const fileInputRef = useRef<HTMLInputElement>(null);

    const focusOptions = [
        { id: "clarity", label: "Clarity", description: "Improve readability" },
        { id: "structure", label: "Structure", description: "Improve organization" },
        { id: "precision", label: "Precision", description: "Technical accuracy" },
        { id: "grammar", label: "Grammar", description: "Fix grammatical errors" },
        { id: "flow", label: "Flow", description: "Improve transitions" },
    ];

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            const ext = file.name.split(".").pop()?.toLowerCase();
            if (!["pdf", "docx", "txt"].includes(ext || "")) {
                setError("Unsupported file type. Please upload PDF, DOCX, or TXT files.");
                return;
            }
            setUploadedFile(file);
            setError(null);

            // For TXT files, read content directly
            if (ext === "txt") {
                const reader = new FileReader();
                reader.onload = (e) => {
                    setDraftText(e.target?.result as string);
                };
                reader.readAsText(file);
            }
        }
    };

    const toggleFocusArea = (area: string) => {
        setFocusAreas((prev) =>
            prev.includes(area) ? prev.filter((a) => a !== area) : [...prev, area]
        );
    };

    const handleRefine = async () => {
        if (!draftText.trim() && !uploadedFile) {
            setError("Please enter draft text or upload a file.");
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            let response;

            if (uploadedFile && !draftText.trim()) {
                // Use file upload endpoint
                const formData = new FormData();
                formData.append("file", uploadedFile);
                formData.append("focus_areas", focusAreas.join(","));
                formData.append("change_level", changeLevel);

                response = await fetch(`${API_URL}/api/draft-conference/refine-file`, {
                    method: "POST",
                    body: formData,
                });
            } else {
                // Use text endpoint
                response = await fetch(`${API_URL}/api/draft-conference/refine`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        text: draftText,
                        focus_areas: focusAreas,
                        change_level: changeLevel,
                    }),
                });
            }

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

            const data: RefineResponse = await response.json();

            if (!data.success || data.error || data.error_message || data.status === "CRASH") {
                setError(data.error || data.error_message || "Refinement failed");
                return;
            }

            // Set original text from response (important for file uploads)
            if (data.original_text && !draftText.trim()) {
                setDraftText(data.original_text);
            }
            
            setRefinedText(data.refined_text);
            setChanges(data.changes || []);
            setChangeSummary(data.change_summary || {});
            setWordCounts({
                original: data.word_count_original,
                refined: data.word_count_refined,
            });
            setWarnings(data.warnings || []);
        } catch (err) {
            // Enhanced error logging for debugging
            console.error("Draft Refinement Error:", err);
            console.error("Error details:", {
                message: err instanceof Error ? err.message : String(err),
                endpoint: uploadedFile ? `${API_URL}/api/draft-conference/refine-file` : `${API_URL}/api/draft-conference/refine`,
                hasFile: !!uploadedFile,
                hasText: !!draftText.trim()
            });
            setError("Failed to connect to the refinement service. Please ensure the backend is running.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleDownload = async (format?: "txt" | "docx" | "pdf") => {
        if (!refinedText) return;

        const downloadFormat = format || exportFormat;

        try {
            if (downloadFormat === "txt") {
                const content = `ORIGINAL TEXT:\n\n${draftText}\n\n${"=".repeat(80)}\n\nREFINED TEXT:\n\n${refinedText}`;
                const blob = new Blob([content], { type: "text/plain" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = uploadedFile
                    ? `refined_${uploadedFile.name.replace(/\.[^/.]+$/, "")}.txt`
                    : "refined_draft.txt";
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            } else {
                // Use backend export endpoint for DOCX and PDF
                try {
                    const response = await fetch(`${API_URL}/api/draft-conference/export/${downloadFormat}`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            original_text: draftText,
                            refined_text: refinedText
                        })
                    });

                    if (!response.ok) {
                        const errorText = await response.text();
                        throw new Error(`Export failed: ${response.statusText} - ${errorText}`);
                    }

                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = `refined_draft.${downloadFormat}`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                } catch (fetchErr) {
                    // Only show error if it's not a successful download
                    console.error("Export error:", fetchErr);
                    // Don't set error state - download might have worked despite error
                }
            }
        } catch (err) {
            // Only log, don't show to user unless critical
            console.error("Export error:", err);
        }
    };

    const toggleChangeAcceptance = (changeId: string) => {
        setChanges(prev =>
            prev.map(change =>
                change.id === changeId
                    ? { ...change, accepted: !change.accepted }
                    : change
            )
        );
    };

    const applyAcceptedChanges = () => {
        let result = draftText;
        changes.forEach(change => {
            if (change.accepted !== false) {
                result = result.replace(change.original, change.refined);
            }
        });
        setRefinedText(result);
    };

    const handleClear = () => {
        setDraftText("");
        setRefinedText("");
        setChanges([]);
        setChangeSummary({});
        setUploadedFile(null);
        setError(null);
        setWarnings([]);
        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };

    return (
        <div className={styles.panel}>
            <div className={styles.header}>
                <div className={styles.titleRow}>
                    <FileEdit size={28} className={styles.icon} />
                    <div>
                        <h1>Draft Refinement</h1>
                        <p>Refine your research draft for submission readiness</p>
                    </div>
                </div>
            </div>

            <div className={styles.content}>
                {/* Input Section */}
                <div className={styles.section}>
                    <h3>Upload Draft</h3>
                    <div className={styles.uploadArea}>
                        <input
                            type="file"
                            ref={fileInputRef}
                            onChange={handleFileUpload}
                            accept=".pdf,.docx,.txt"
                            className={styles.fileInput}
                            id="draft-upload"
                        />
                        <label htmlFor="draft-upload" className={styles.uploadLabel}>
                            <Upload size={24} />
                            <span>{uploadedFile ? uploadedFile.name : "Upload PDF, DOCX, or TXT"}</span>
                        </label>
                        {uploadedFile && (
                            <button className={styles.clearFile} onClick={() => {
                                setUploadedFile(null);
                                if (fileInputRef.current) fileInputRef.current.value = "";
                            }}>
                                <X size={16} />
                            </button>
                        )}
                    </div>

                    <div className={styles.orDivider}>
                        <span>or paste text directly</span>
                    </div>

                    <textarea
                        className={styles.textArea}
                        placeholder="Paste your draft text here..."
                        value={draftText}
                        onChange={(e) => setDraftText(e.target.value)}
                        rows={10}
                    />
                </div>

                {/* Options Section */}
                <div className={styles.section}>
                    <h3>Refinement Options</h3>

                    <div className={styles.optionGroup}>
                        <label>Focus Areas</label>
                        <div className={styles.focusGrid}>
                            {focusOptions.map((opt) => (
                                <button
                                    key={opt.id}
                                    className={`${styles.focusBtn} ${focusAreas.includes(opt.id) ? styles.active : ""}`}
                                    onClick={() => toggleFocusArea(opt.id)}
                                >
                                    <span className={styles.focusLabel}>{opt.label}</span>
                                    <span className={styles.focusDesc}>{opt.description}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className={styles.optionGroup}>
                        <label>Change Intensity</label>
                        <div className={styles.levelSelector}>
                            {(["light", "moderate", "thorough"] as const).map((level) => (
                                <button
                                    key={level}
                                    className={`${styles.levelBtn} ${changeLevel === level ? styles.active : ""}`}
                                    onClick={() => setChangeLevel(level)}
                                >
                                    {level.charAt(0).toUpperCase() + level.slice(1)}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Action Buttons */}
                <div className={styles.actions}>
                    <button
                        className={styles.refineBtn}
                        onClick={handleRefine}
                        disabled={isLoading || (!draftText.trim() && !uploadedFile)}
                    >
                        {isLoading ? (
                            <>
                                <RefreshCw size={20} className={styles.spin} />
                                Refining...
                            </>
                        ) : (
                            <>
                                <Sparkles size={20} />
                                Refine Draft
                            </>
                        )}
                    </button>
                    <button className={styles.clearBtn} onClick={handleClear}>
                        Clear All
                    </button>
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

                {/* Results Section */}
                <AnimatePresence>
                    {refinedText && (
                        <motion.div
                            className={styles.results}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                        >
                            <div className={styles.resultHeader}>
                                <div className={styles.resultTitle}>
                                    <CheckCircle size={24} className={styles.successIcon} />
                                    <h3>Refinement Complete</h3>
                                </div>
                                <div className={styles.headerActions}>
                                    <div className={styles.viewToggle}>
                                        <button
                                            className={viewMode === "refined" ? styles.active : ""}
                                            onClick={() => setViewMode("refined")}
                                        >
                                            Refined
                                        </button>
                                        <button
                                            className={viewMode === "split" ? styles.active : ""}
                                            onClick={() => setViewMode("split")}
                                        >
                                            Compare
                                        </button>
                                    </div>
                                    <div className={styles.exportDropdown}>
                                        <button
                                            className={styles.downloadBtn}
                                            onClick={() => setShowExportMenu(!showExportMenu)}
                                        >
                                            <Download size={18} />
                                            Export
                                        </button>
                                        {showExportMenu && (
                                            <div className={styles.exportMenu}>
                                                <button onClick={() => { handleDownload("txt"); setShowExportMenu(false); }}>
                                                    Text (.txt)
                                                </button>
                                                <button onClick={() => { handleDownload("docx"); setShowExportMenu(false); }}>
                                                    Word (.docx)
                                                </button>
                                                <button onClick={() => { handleDownload("pdf"); setShowExportMenu(false); }}>
                                                    PDF (.pdf)
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>

                            {/* Stats */}
                            <div className={styles.stats}>
                                <div className={styles.stat}>
                                    <span className={styles.statLabel}>Original</span>
                                    <span className={styles.statValue}>{wordCounts.original} words</span>
                                </div>
                                <div className={styles.stat}>
                                    <span className={styles.statLabel}>Refined</span>
                                    <span className={styles.statValue}>{wordCounts.refined} words</span>
                                </div>
                                <div className={styles.stat}>
                                    <span className={styles.statLabel}>Changes</span>
                                    <span className={styles.statValue}>{changes.length} improvements</span>
                                </div>
                            </div>

                            {/* Change Summary */}
                            {Object.keys(changeSummary).length > 0 && (
                                <div className={styles.changeSummary}>
                                    {Object.entries(changeSummary).map(([type, count]) => (
                                        <span key={type} className={styles.changeTag}>
                                            {type}: {count}
                                        </span>
                                    ))}
                                </div>
                            )}

                            {/* Refined Text or Split View */}
                            {viewMode === "refined" ? (
                                <div className={styles.refinedOutput}>
                                    <div className={styles.outputHeader}>
                                        <FileText size={18} />
                                        <span>Refined Draft</span>
                                    </div>
                                    <div className={styles.outputText}>{refinedText}</div>
                                </div>
                            ) : (
                                <div className={styles.splitView}>
                                    <div className={styles.splitColumn}>
                                        <div className={styles.outputHeader}>
                                            <FileText size={18} />
                                            <span>Original</span>
                                        </div>
                                        <div className={styles.outputText}>{draftText}</div>
                                    </div>
                                    <div className={styles.splitColumn}>
                                        <div className={styles.outputHeader}>
                                            <FileText size={18} />
                                            <span>Refined</span>
                                        </div>
                                        <div className={styles.outputText}>{refinedText}</div>
                                    </div>
                                </div>
                            )}

                            {/* Changes Accordion */}
                            {changes.length > 0 && (
                                <div className={styles.changesSection}>
                                    <button
                                        className={styles.changesToggle}
                                        onClick={() => setShowChanges(!showChanges)}
                                    >
                                        <span>View Detailed Changes ({changes.length})</span>
                                        {showChanges ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                                    </button>
                                    <AnimatePresence>
                                        {showChanges && (
                                            <motion.div
                                                className={styles.changesList}
                                                initial={{ height: 0, opacity: 0 }}
                                                animate={{ height: "auto", opacity: 1 }}
                                                exit={{ height: 0, opacity: 0 }}
                                            >
                                                {changes.map((change, idx) => (
                                                    <div key={idx} className={styles.changeItem}>
                                                        <div className={styles.changeHeader}>
                                                            <div className={styles.changeType}>{change.type}</div>
                                                            <button
                                                                className={`${styles.acceptBtn} ${change.accepted !== false ? styles.accepted : ""}`}
                                                                onClick={() => toggleChangeAcceptance(change.id || `change-${idx}`)}
                                                                title={change.accepted !== false ? "Click to reject" : "Click to accept"}
                                                            >
                                                                {change.accepted !== false ? <CheckCircle size={16} /> : <X size={16} />}
                                                            </button>
                                                        </div>
                                                        <div className={styles.changeContent}>
                                                            <div className={styles.original}>
                                                                <span className={styles.label}>Original:</span>
                                                                <span>{change.original}</span>
                                                            </div>
                                                            <div className={styles.refined}>
                                                                <span className={styles.label}>Refined:</span>
                                                                <span>{change.refined}</span>
                                                            </div>
                                                            <div className={styles.reason}>
                                                                <span className={styles.label}>Reason:</span>
                                                                <span>{change.reason}</span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                ))}
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                </div>
                            )}

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

            {/* Constraints Notice */}
            <div className={styles.notice}>
                <AlertTriangle size={16} />
                <span>
                    This tool preserves your original intent. No new ideas, claims, or data are introduced.
                    Output is natural and human-readable.
                </span>
            </div>
        </div>
    );
}
