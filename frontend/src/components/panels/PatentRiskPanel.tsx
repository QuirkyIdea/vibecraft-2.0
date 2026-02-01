"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    FileSearch,
    Send,
    Loader2,
    AlertTriangle,
    Shield,
    XCircle,
} from "lucide-react";
import {
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    Radar,
    ResponsiveContainer,
} from "recharts";
import { useStats } from "@/context/StatsContext";
import PDFUpload from "@/components/PDFUpload";
import styles from "./PatentRiskPanel.module.css";

interface RiskIndicators {
    novelty_risk: number;
    scope_risk: number;
    clarity_risk: number;
    prior_art_risk: number;
    overall_risk: number;
}

interface RiskResult {
    risk_indicators: RiskIndicators;
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

export default function PatentRiskPanel() {
    const { recordPatentScan } = useStats();
    const [claimText, setClaimText] = useState("");
    const [claimType, setClaimType] = useState<"independent" | "dependent">(
        "independent"
    );
    const [domain, setDomain] = useState("");
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [result, setResult] = useState<RiskResult | null>(null);
    const [error, setError] = useState<CrashLog | null>(null);

    const scanRisk = async () => {
        if (!claimText.trim() || claimText.length < 20) return;

        setIsAnalyzing(true);
        setResult(null);
        setError(null);

        try {
            const response = await fetch("http://localhost:8000/api/patent/risk-scan", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    claim_text: claimText,
                    claim_type: claimType,
                    domain: domain || undefined,
                }),
            });

            const data = await response.json();

            if (data.status === "CRASH") {
                setError(data as CrashLog);
            } else {
                const riskResult = data as RiskResult;
                setResult(riskResult);
                // Record stats
                recordPatentScan(claimText, riskResult.risk_indicators.overall_risk);
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

    const getRiskLevel = (risk: number): { label: string; color: string } => {
        if (risk >= 0.7) return { label: "HIGH", color: "var(--error)" };
        if (risk >= 0.4) return { label: "MEDIUM", color: "var(--warning)" };
        return { label: "LOW", color: "var(--success)" };
    };

    const getRadarData = () => {
        if (!result) return [];
        return [
            {
                subject: "Novelty",
                value: result.risk_indicators.novelty_risk * 100,
                fullMark: 100,
            },
            {
                subject: "Scope",
                value: result.risk_indicators.scope_risk * 100,
                fullMark: 100,
            },
            {
                subject: "Clarity",
                value: result.risk_indicators.clarity_risk * 100,
                fullMark: 100,
            },
            {
                subject: "Prior Art",
                value: result.risk_indicators.prior_art_risk * 100,
                fullMark: 100,
            },
        ];
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <div className={styles.headerIcon}>
                    <FileSearch size={24} />
                </div>
                <div>
                    <h1>Patent Risk Scanner</h1>
                    <p>
                        Analyze patent claims for risk indicators and potential vulnerabilities
                    </p>
                </div>
            </div>

            <div className={styles.mainContent}>
                <div className={styles.inputSection}>
                    <div className={styles.card}>
                        <h3>Enter Patent Claim</h3>

                        {/* PDF Upload */}
                        <div className={styles.inputGroup}>
                            <label className="label">Upload Patent PDF (optional)</label>
                            <PDFUpload
                                onTextExtracted={(text) => {
                                    setClaimText(prev => prev + (prev ? "\n\n" : "") + text);
                                }}
                                compact
                            />
                        </div>

                        <div className={styles.divider}>
                            <span>or enter claim manually</span>
                        </div>

                        <div className={styles.inputGroup}>
                            <label className="label">Claim Text *</label>
                            <textarea
                                className={`input ${styles.claimInput}`}
                                placeholder="Enter the patent claim text to analyze. Include all claim elements and limitations."
                                value={claimText}
                                onChange={(e) => setClaimText(e.target.value)}
                            />
                            <span className={styles.charCount}>{claimText.length} characters (min 20)</span>
                        </div>

                        <div className={styles.inputRow}>
                            <div className={styles.inputGroup}>
                                <label className="label">Claim Type</label>
                                <select
                                    className="input"
                                    value={claimType}
                                    onChange={(e) =>
                                        setClaimType(e.target.value as "independent" | "dependent")
                                    }
                                >
                                    <option value="independent">Independent Claim</option>
                                    <option value="dependent">Dependent Claim</option>
                                </select>
                            </div>
                            <div className={styles.inputGroup}>
                                <label className="label">Technology Domain</label>
                                <input
                                    className="input"
                                    placeholder="e.g., Software, Biotech"
                                    value={domain}
                                    onChange={(e) => setDomain(e.target.value)}
                                />
                            </div>
                        </div>

                        <button
                            className={`btn btn-primary ${styles.scanBtn}`}
                            onClick={scanRisk}
                            disabled={isAnalyzing || claimText.length < 20}
                        >
                            {isAnalyzing ? (
                                <>
                                    <Loader2 size={18} className={styles.spinner} />
                                    Scanning...
                                </>
                            ) : (
                                <>
                                    <Shield size={18} />
                                    Scan Risk
                                </>
                            )}
                        </button>

                        <div className={styles.disclaimer}>
                            <AlertTriangle size={14} />
                            <span>
                                Risk scores are probabilistic estimates. This does NOT constitute
                                legal advice or patentability assessment.
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
                                <div className={styles.scanAnimation}>
                                    {[...Array(5)].map((_, i) => (
                                        <motion.div
                                            key={i}
                                            className={styles.scanLine}
                                            animate={{
                                                scaleX: [0, 1, 0],
                                                opacity: [0, 1, 0],
                                            }}
                                            transition={{
                                                duration: 1.5,
                                                repeat: Infinity,
                                                delay: i * 0.2,
                                            }}
                                        />
                                    ))}
                                </div>
                                <p>Scanning for risk indicators...</p>
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
                                    <h3>Scan Failed</h3>
                                </div>
                                <p>{error.error_message}</p>
                                <code>Stage: {error.failed_stage}</code>
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
                                <div className={styles.overallRisk}>
                                    <div className={styles.riskMeter}>
                                        <svg className={styles.riskGauge} viewBox="0 0 200 100">
                                            <defs>
                                                <linearGradient
                                                    id="riskGradient"
                                                    x1="0%"
                                                    y1="0%"
                                                    x2="100%"
                                                    y2="0%"
                                                >
                                                    <stop offset="0%" stopColor="var(--success)" />
                                                    <stop offset="50%" stopColor="var(--warning)" />
                                                    <stop offset="100%" stopColor="var(--error)" />
                                                </linearGradient>
                                            </defs>
                                            <path
                                                d="M 20 90 A 80 80 0 0 1 180 90"
                                                fill="none"
                                                stroke="var(--bg-tertiary)"
                                                strokeWidth="16"
                                                strokeLinecap="round"
                                            />
                                            <path
                                                d="M 20 90 A 80 80 0 0 1 180 90"
                                                fill="none"
                                                stroke="url(#riskGradient)"
                                                strokeWidth="16"
                                                strokeLinecap="round"
                                                strokeDasharray={`${result.risk_indicators.overall_risk * 251} 251`}
                                            />
                                            <motion.circle
                                                cx={20 + result.risk_indicators.overall_risk * 160}
                                                cy={90 - Math.sin(result.risk_indicators.overall_risk * Math.PI) * 80}
                                                r="8"
                                                fill={getRiskLevel(result.risk_indicators.overall_risk).color}
                                                initial={{ scale: 0 }}
                                                animate={{ scale: 1 }}
                                                transition={{ delay: 0.5 }}
                                            />
                                        </svg>
                                        <div className={styles.riskValue}>
                                            <span
                                                style={{
                                                    color: getRiskLevel(result.risk_indicators.overall_risk).color,
                                                }}
                                            >
                                                {(result.risk_indicators.overall_risk * 100).toFixed(0)}%
                                            </span>
                                            <span className={styles.riskLabel}>Overall Risk</span>
                                        </div>
                                    </div>
                                    <span
                                        className={styles.riskBadge}
                                        style={{
                                            background: `${getRiskLevel(result.risk_indicators.overall_risk).color}20`,
                                            color: getRiskLevel(result.risk_indicators.overall_risk).color,
                                            borderColor: getRiskLevel(result.risk_indicators.overall_risk).color,
                                        }}
                                    >
                                        {getRiskLevel(result.risk_indicators.overall_risk).label} RISK
                                    </span>
                                </div>

                                <div className={styles.radarSection}>
                                    <h4>Risk Breakdown</h4>
                                    <div className={styles.radarChart}>
                                        <ResponsiveContainer width="100%" height={250}>
                                            <RadarChart data={getRadarData()}>
                                                <PolarGrid stroke="var(--border-subtle)" />
                                                <PolarAngleAxis
                                                    dataKey="subject"
                                                    tick={{ fill: "var(--text-secondary)", fontSize: 12 }}
                                                />
                                                <PolarRadiusAxis
                                                    angle={30}
                                                    domain={[0, 100]}
                                                    tick={{ fill: "var(--text-muted)", fontSize: 10 }}
                                                />
                                                <Radar
                                                    name="Risk"
                                                    dataKey="value"
                                                    stroke="var(--accent-primary)"
                                                    fill="var(--accent-primary)"
                                                    fillOpacity={0.3}
                                                />
                                            </RadarChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>

                                <div className={styles.riskDetails}>
                                    {Object.entries(result.risk_indicators)
                                        .filter(([key]) => key !== "overall_risk")
                                        .map(([key, value]) => (
                                            <div key={key} className={styles.riskItem}>
                                                <div className={styles.riskItemHeader}>
                                                    <span>{key.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())}</span>
                                                    <span style={{ color: getRiskLevel(value).color }}>
                                                        {(value * 100).toFixed(0)}%
                                                    </span>
                                                </div>
                                                <div className="progress-bar">
                                                    <div
                                                        className="progress-fill"
                                                        style={{
                                                            width: `${value * 100}%`,
                                                            background: getRiskLevel(value).color,
                                                        }}
                                                    />
                                                </div>
                                            </div>
                                        ))}
                                </div>

                                <div className={`${styles.card} ${styles.unknownsCard}`}>
                                    <h4>
                                        <AlertTriangle size={16} />
                                        Limitations & Unknowns
                                    </h4>
                                    <ul>
                                        {result.unknowns.map((unknown, i) => (
                                            <li key={i}>{unknown}</li>
                                        ))}
                                    </ul>
                                </div>

                                <div className={`${styles.card} ${styles.disclaimerBox}`}>
                                    <Shield size={16} />
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
                                <FileSearch size={64} className={styles.emptyIcon} />
                                <h3>Ready to Scan</h3>
                                <p>Enter a patent claim to analyze risk indicators</p>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </div>
    );
}
