"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";

interface AnalysisRecord {
    id: string;
    type: "idea" | "patent";
    timestamp: string;
    confidence?: number;
    riskLevel?: number;
    title: string;
}

interface StatsContextType {
    ideasAnalyzed: number;
    patentScans: number;
    riskAlerts: number;
    avgConfidence: number | null;
    recentActivity: AnalysisRecord[];
    recordIdeaAnalysis: (title: string, confidence: number) => void;
    recordPatentScan: (title: string, riskLevel: number) => void;
}

const StatsContext = createContext<StatsContextType | undefined>(undefined);

const STORAGE_KEY = "inventix_stats";

export function StatsProvider({ children }: { children: ReactNode }) {
    const [ideasAnalyzed, setIdeasAnalyzed] = useState(0);
    const [patentScans, setPatentScans] = useState(0);
    const [riskAlerts, setRiskAlerts] = useState(0);
    const [avgConfidence, setAvgConfidence] = useState<number | null>(null);
    const [recentActivity, setRecentActivity] = useState<AnalysisRecord[]>([]);
    const [confidenceHistory, setConfidenceHistory] = useState<number[]>([]);

    // Load from localStorage on mount
    useEffect(() => {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            try {
                const data = JSON.parse(stored);
                setIdeasAnalyzed(data.ideasAnalyzed || 0);
                setPatentScans(data.patentScans || 0);
                setRiskAlerts(data.riskAlerts || 0);
                setAvgConfidence(data.avgConfidence || null);
                setRecentActivity(data.recentActivity || []);
                setConfidenceHistory(data.confidenceHistory || []);
            } catch (e) {
                console.error("Failed to load stats:", e);
            }
        }
    }, []);

    // Save to localStorage on change
    useEffect(() => {
        const data = {
            ideasAnalyzed,
            patentScans,
            riskAlerts,
            avgConfidence,
            recentActivity,
            confidenceHistory,
        };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    }, [ideasAnalyzed, patentScans, riskAlerts, avgConfidence, recentActivity, confidenceHistory]);

    const recordIdeaAnalysis = (title: string, confidence: number) => {
        setIdeasAnalyzed((prev) => prev + 1);

        const newHistory = [...confidenceHistory, confidence];
        setConfidenceHistory(newHistory);
        setAvgConfidence(newHistory.reduce((a, b) => a + b, 0) / newHistory.length);

        const record: AnalysisRecord = {
            id: `idea-${Date.now()}`,
            type: "idea",
            timestamp: new Date().toISOString(),
            confidence,
            title: title.substring(0, 50) + (title.length > 50 ? "..." : ""),
        };
        setRecentActivity((prev) => [record, ...prev].slice(0, 10));
    };

    const recordPatentScan = (title: string, riskLevel: number) => {
        setPatentScans((prev) => prev + 1);

        if (riskLevel >= 0.7) {
            setRiskAlerts((prev) => prev + 1);
        }

        const record: AnalysisRecord = {
            id: `patent-${Date.now()}`,
            type: "patent",
            timestamp: new Date().toISOString(),
            riskLevel,
            title: title.substring(0, 50) + (title.length > 50 ? "..." : ""),
        };
        setRecentActivity((prev) => [record, ...prev].slice(0, 10));
    };

    return (
        <StatsContext.Provider
            value={{
                ideasAnalyzed,
                patentScans,
                riskAlerts,
                avgConfidence,
                recentActivity,
                recordIdeaAnalysis,
                recordPatentScan,
            }}
        >
            {children}
        </StatsContext.Provider>
    );
}

export function useStats() {
    const context = useContext(StatsContext);
    if (!context) {
        throw new Error("useStats must be used within a StatsProvider");
    }
    return context;
}
