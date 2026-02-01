"use client";

import React, { createContext, useContext, useState, useCallback, ReactNode } from "react";
import { authFetch } from "./AuthContext";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Types
export type ProjectType = "patent" | "research";
export type NoveltyStatus = "red" | "yellow" | "green" | "unknown";
export type PipelineStage = "idle" | "ingesting" | "extracting" | "analyzing" | "validating" | "complete" | "error";

export interface ProjectCard {
    id: string;
    title: string;
    project_type: ProjectType;
    novelty_status: NoveltyStatus;
    progress: number;
    last_analyzed?: string;
    created_at: string;
}

export interface PriorArtMatch {
    patent_id?: string;
    title?: string;
    summary?: string;
    similarity?: number;
    relevance?: number;
    overlap_areas?: string[];
}

export interface NovelClaim {
    claim: string;
    evidence?: string;
    confidence?: number;
}

export interface Recommendation {
    title?: string;
    description: string;
    priority?: "high" | "medium" | "low";
}

export interface ProjectAnalysis {
    novelty_score: number;
    novelty_status: NoveltyStatus;
    confidence_score?: number;
    confidence?: string;
    risk_level?: "low" | "medium" | "high";
    risk_factors?: string[];
    risk_summary?: string;
    key_concepts: string[];
    potential_overlaps: string[];
    novel_claims?: NovelClaim[] | string[];
    prior_art_matches?: PriorArtMatch[];
    recommendations?: Recommendation[] | string[];
    summary?: string;
}

export interface Project {
    id: string;
    user_id: string;
    title: string;
    description: string;
    project_type: ProjectType;
    document_text?: string;
    created_at: string;
    updated_at: string;
    last_analyzed?: string;
    analysis?: ProjectAnalysis;
    pipeline_stage: PipelineStage;
    progress: number;
}

export interface RoadmapMilestone {
    id: string;
    title: string;
    description: string;
    target_date?: string;
    completed: boolean;
    completed_at?: string;
    order: number;
}

export interface RoadmapPhase {
    id: string;
    name: string;
    description: string;
    milestones: RoadmapMilestone[];
    color: string;
}

export interface Roadmap {
    project_id: string;
    phases: RoadmapPhase[];
    created_at: string;
    updated_at: string;
}

export interface PipelineNode {
    id: string;
    name: string;
    status: "idle" | "active" | "complete" | "error";
    progress: number;
    message?: string;
}

export interface PipelineStatus {
    project_id: string;
    current_stage: PipelineStage;
    overall_progress: number;
    nodes: PipelineNode[];
    started_at?: string;
    completed_at?: string;
    error_message?: string;
}

interface ProjectContextType {
    projects: ProjectCard[];
    selectedProject: Project | null;
    roadmap: Roadmap | null;
    pipelineStatus: PipelineStatus | null;
    isLoading: boolean;
    error: string | null;

    // Actions
    fetchProjects: () => Promise<void>;
    createProject: (data: { title: string; description: string; project_type: ProjectType; document_text?: string }) => Promise<Project | null>;
    selectProject: (projectId: string) => Promise<void>;
    analyzeProject: (projectId: string) => Promise<void>;
    deleteProject: (projectId: string) => Promise<boolean>;
    fetchRoadmap: (projectId: string) => Promise<void>;
    updateMilestone: (projectId: string, phaseId: string, milestoneId: string, completed: boolean) => Promise<void>;
    fetchPipelineStatus: (projectId: string) => Promise<void>;
    clearSelectedProject: () => void;
}

const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

export function ProjectProvider({ children }: { children: ReactNode }) {
    const [projects, setProjects] = useState<ProjectCard[]>([]);
    const [selectedProject, setSelectedProject] = useState<Project | null>(null);
    const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
    const [pipelineStatus, setPipelineStatus] = useState<PipelineStatus | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchProjects = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await authFetch(`${API_URL}/api/projects`);
            if (!response.ok) throw new Error("Failed to fetch projects");
            const data = await response.json();
            setProjects(data.projects || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to fetch projects");
            setProjects([]);
        } finally {
            setIsLoading(false);
        }
    }, []);

    const createProject = useCallback(async (data: {
        title: string;
        description: string;
        project_type: ProjectType;
        document_text?: string;
    }): Promise<Project | null> => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await authFetch(`${API_URL}/api/projects`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error("Failed to create project");
            const project = await response.json();
            await fetchProjects(); // Refresh list
            return project;
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to create project");
            return null;
        } finally {
            setIsLoading(false);
        }
    }, [fetchProjects]);

    const selectProject = useCallback(async (projectId: string) => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await authFetch(`${API_URL}/api/projects/${projectId}`);
            if (!response.ok) throw new Error("Failed to fetch project");
            const project = await response.json();
            setSelectedProject(project);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to fetch project");
        } finally {
            setIsLoading(false);
        }
    }, []);

    const analyzeProject = useCallback(async (projectId: string) => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await authFetch(`${API_URL}/api/projects/${projectId}/analyze`, {
                method: "POST"
            });
            if (!response.ok) throw new Error("Failed to analyze project");
            const project = await response.json();
            setSelectedProject(project);
            await fetchProjects(); // Refresh list to update status
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to analyze project");
        } finally {
            setIsLoading(false);
        }
    }, [fetchProjects]);

    const deleteProject = useCallback(async (projectId: string): Promise<boolean> => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await authFetch(`${API_URL}/api/projects/${projectId}`, {
                method: "DELETE"
            });
            if (!response.ok) throw new Error("Failed to delete project");
            await fetchProjects();
            if (selectedProject?.id === projectId) {
                setSelectedProject(null);
            }
            return true;
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to delete project");
            return false;
        } finally {
            setIsLoading(false);
        }
    }, [fetchProjects, selectedProject]);

    const fetchRoadmap = useCallback(async (projectId: string) => {
        try {
            const response = await authFetch(`${API_URL}/api/projects/${projectId}/roadmap`);
            if (!response.ok) throw new Error("Failed to fetch roadmap");
            const data = await response.json();
            setRoadmap(data);
        } catch (err) {
            console.error("Roadmap fetch error:", err);
        }
    }, []);

    const updateMilestone = useCallback(async (
        projectId: string,
        phaseId: string,
        milestoneId: string,
        completed: boolean
    ) => {
        try {
            const response = await authFetch(
                `${API_URL}/api/projects/${projectId}/roadmap/${phaseId}/milestones/${milestoneId}?completed=${completed}`,
                { method: "PATCH" }
            );
            if (!response.ok) throw new Error("Failed to update milestone");
            const data = await response.json();
            setRoadmap(data);
        } catch (err) {
            console.error("Milestone update error:", err);
        }
    }, []);

    const fetchPipelineStatus = useCallback(async (projectId: string) => {
        try {
            const response = await authFetch(`${API_URL}/api/projects/${projectId}/pipeline`);
            if (!response.ok) throw new Error("Failed to fetch pipeline status");
            const data = await response.json();
            setPipelineStatus(data);
        } catch (err) {
            console.error("Pipeline status fetch error:", err);
        }
    }, []);

    const clearSelectedProject = useCallback(() => {
        setSelectedProject(null);
        setRoadmap(null);
        setPipelineStatus(null);
    }, []);

    return (
        <ProjectContext.Provider
            value={{
                projects,
                selectedProject,
                roadmap,
                pipelineStatus,
                isLoading,
                error,
                fetchProjects,
                createProject,
                selectProject,
                analyzeProject,
                deleteProject,
                fetchRoadmap,
                updateMilestone,
                fetchPipelineStatus,
                clearSelectedProject
            }}
        >
            {children}
        </ProjectContext.Provider>
    );
}

export function useProjects() {
    const context = useContext(ProjectContext);
    if (!context) {
        throw new Error("useProjects must be used within a ProjectProvider");
    }
    return context;
}
