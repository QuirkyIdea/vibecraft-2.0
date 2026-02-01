"use client";

import { motion } from "framer-motion";
import {
    Activity,
    TrendingUp,
    FileSearch,
    Lightbulb,
    AlertCircle,
    CheckCircle,
    Clock,
} from "lucide-react";
import { useStats } from "@/context/StatsContext";
import styles from "./DashboardOverview.module.css";

export default function DashboardOverview() {
    const { ideasAnalyzed, patentScans, riskAlerts, avgConfidence, recentActivity } = useStats();

    const stats = [
        {
            label: "Ideas Analyzed",
            value: ideasAnalyzed.toString(),
            change: ideasAnalyzed > 0 ? `+${ideasAnalyzed}` : "+0%",
            icon: Lightbulb,
            color: "var(--accent-primary)",
        },
        {
            label: "Patent Scans",
            value: patentScans.toString(),
            change: patentScans > 0 ? `+${patentScans}` : "+0%",
            icon: FileSearch,
            color: "var(--accent-secondary)",
        },
        {
            label: "Risk Alerts",
            value: riskAlerts.toString(),
            change: riskAlerts.toString(),
            icon: AlertCircle,
            color: "var(--warning)",
        },
        {
            label: "Confidence Avg",
            value: avgConfidence !== null ? `${(avgConfidence * 100).toFixed(0)}%` : "N/A",
            change: avgConfidence !== null ? "—" : "—",
            icon: Activity,
            color: "var(--success)",
        },
    ];

    const formatTime = (timestamp: string) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const minutes = Math.floor(diff / 60000);
        if (minutes < 1) return "Just now";
        if (minutes < 60) return `${minutes}m ago`;
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `${hours}h ago`;
        return date.toLocaleDateString();
    };

    return (
        <div className={styles.dashboard}>
            <div className={styles.header}>
                <div className={styles.headerContent}>
                    <h1>Dashboard</h1>
                    <p>Evidence-Locked Research & Patent Intelligence Overview</p>
                </div>
                <div className={styles.systemStatus}>
                    <div className={styles.statusItem}>
                        <CheckCircle size={16} className={styles.statusIconSuccess} />
                        <span>API Connected</span>
                    </div>
                    <div className={styles.statusItem}>
                        <Clock size={16} className={styles.statusIconMuted} />
                        <span>Last sync: Just now</span>
                    </div>
                </div>
            </div>

            <div className={styles.statsGrid}>
                {stats.map((stat, index) => {
                    const Icon = stat.icon;
                    return (
                        <motion.div
                            key={stat.label}
                            className={styles.statCard}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                        >
                            <div className={styles.statIcon} style={{ color: stat.color }}>
                                <Icon size={24} />
                            </div>
                            <div className={styles.statContent}>
                                <span className={styles.statValue}>{stat.value}</span>
                                <span className={styles.statLabel}>{stat.label}</span>
                            </div>
                            <span
                                className={styles.statChange}
                                style={{
                                    color: stat.change.startsWith("+") && stat.change !== "+0%"
                                        ? "var(--success)"
                                        : "var(--text-muted)",
                                }}
                            >
                                {stat.change}
                            </span>
                        </motion.div>
                    );
                })}
            </div>

            <div className={styles.mainGrid}>
                <motion.div
                    className={`${styles.card} ${styles.welcomeCard}`}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.3 }}
                >
                    <div className={styles.welcomeContent}>
                        <h2>Welcome to Inventix AI</h2>
                        <p>
                            ANTIGRAVITY is your evidence-locked intelligence companion for research
                            and patent analysis. Start by analyzing an idea or scanning a patent
                            claim for novelty indicators.
                        </p>
                        <div className={styles.featureList}>
                            <div className={styles.feature}>
                                <Lightbulb size={20} />
                                <span>Analyze innovation ideas for novelty signals</span>
                            </div>
                            <div className={styles.feature}>
                                <FileSearch size={20} />
                                <span>Scan patent claims for risk indicators</span>
                            </div>
                            <div className={styles.feature}>
                                <TrendingUp size={20} />
                                <span>Track research progress with probabilistic metrics</span>
                            </div>
                        </div>
                    </div>
                    <div className={styles.welcomeVisual}>
                        <motion.div
                            className={styles.orb}
                            animate={{
                                scale: [1, 1.1, 1],
                                opacity: [0.5, 0.8, 0.5],
                            }}
                            transition={{ duration: 4, repeat: Infinity }}
                        />
                        <motion.div
                            className={styles.orbRing}
                            animate={{ rotate: 360 }}
                            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                        />
                    </div>
                </motion.div>

                <motion.div
                    className={`${styles.card} ${styles.disclaimerCard}`}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 }}
                >
                    <AlertCircle size={24} className={styles.disclaimerIcon} />
                    <h3>System Boundaries</h3>
                    <ul className={styles.disclaimerList}>
                        <li>All outputs are probabilistic estimates</li>
                        <li>This system does NOT determine patentability</li>
                        <li>This system does NOT provide legal advice</li>
                        <li>Human review is always required</li>
                        <li>Evidence references are mandatory in all outputs</li>
                    </ul>
                    <div className={styles.priorityList}>
                        <span className={styles.priorityItem}>Accuracy &gt; Coverage</span>
                        <span className={styles.priorityItem}>Evidence &gt; Eloquence</span>
                        <span className={styles.priorityItem}>Transparency &gt; Usefulness</span>
                    </div>
                </motion.div>
            </div>

            <motion.div
                className={`${styles.card} ${styles.activityCard}`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
            >
                <h3>Recent Activity</h3>
                {recentActivity.length === 0 ? (
                    <div className={styles.emptyState}>
                        <Activity size={48} className={styles.emptyIcon} />
                        <p>No activity yet. Start by analyzing an idea or patent claim.</p>
                    </div>
                ) : (
                    <div className={styles.activityList}>
                        {recentActivity.map((record) => (
                            <div key={record.id} className={styles.activityItem}>
                                <div
                                    className={styles.activityIcon}
                                    style={{
                                        color: record.type === "idea"
                                            ? "var(--accent-primary)"
                                            : "var(--accent-secondary)"
                                    }}
                                >
                                    {record.type === "idea" ? <Lightbulb size={18} /> : <FileSearch size={18} />}
                                </div>
                                <div className={styles.activityContent}>
                                    <span className={styles.activityTitle}>{record.title}</span>
                                    <span className={styles.activityMeta}>
                                        {record.type === "idea" ? "Idea Analysis" : "Patent Scan"} • {formatTime(record.timestamp)}
                                    </span>
                                </div>
                                <div className={styles.activityScore}>
                                    {record.type === "idea" && record.confidence !== undefined && (
                                        <span style={{ color: "var(--success)" }}>
                                            {(record.confidence * 100).toFixed(0)}%
                                        </span>
                                    )}
                                    {record.type === "patent" && record.riskLevel !== undefined && (
                                        <span style={{
                                            color: record.riskLevel >= 0.7
                                                ? "var(--error)"
                                                : record.riskLevel >= 0.4
                                                    ? "var(--warning)"
                                                    : "var(--success)"
                                        }}>
                                            {(record.riskLevel * 100).toFixed(0)}% Risk
                                        </span>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </motion.div>
        </div>
    );
}
