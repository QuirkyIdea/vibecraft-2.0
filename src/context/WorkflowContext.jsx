/**
 * Inventix AI - Workflow Context
 * 
 * REFACTORED: All mock data removed. Now connected to real backend API.
 * This manages the global application state for projects and workflow stages.
 */
import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../api/endpoints';

const WorkflowContext = createContext();

export const useWorkflow = () => useContext(WorkflowContext);

export const WorkflowProvider = ({ children }) => {
    // Views: 'HOME', 'DASHBOARD'
    const [currentView, setCurrentView] = useState('HOME');

    // Projects - Now fetched from backend
    const [projects, setProjects] = useState([]);
    const [projectsLoading, setProjectsLoading] = useState(false);
    const [projectsError, setProjectsError] = useState(null);

    // Active Project State (null = Project List View)
    const [activeProject, setActiveProject] = useState(null);
    const [activeProjectLoading, setActiveProjectLoading] = useState(false);

    // New Project Creation Flow State
    // Stages: 'IDLE', 'TYPE', 'IDEA', 'UPLOAD', 'PROCESSING', 'ACTIVE'
    const [creationStage, setCreationStage] = useState('IDLE');
    const [newProjectData, setNewProjectData] = useState({ 
        title: '', 
        description: '', 
        outcome: '', 
        domain: null, 
        projectType: 'RESEARCH' 
    });

    // System Status
    const [systemStatus, setSystemStatus] = useState(null);

    // ========== Fetch Projects from Backend ==========
    const fetchProjects = useCallback(async () => {
        setProjectsLoading(true);
        setProjectsError(null);
        try {
            const response = await api.projects.list();
            // Transform backend response to match UI expectations
            const transformedProjects = response.data.map(p => ({
                id: p.id,
                title: p.title,
                type: p.type,
                status: p.analysis_state?.status || 'Created',
                domain: p.domain || 'General',
                createdAt: p.created_at,
                ideaText: p.idea_text,
                noveltyRisk: p.analysis_state?.novelty_risk,
                evidenceCount: p.evidence_count || 0,
            }));
            setProjects(transformedProjects);
        } catch (error) {
            console.error('Failed to fetch projects:', error);
            setProjectsError('Failed to load projects. Is the backend running?');
            setProjects([]);
        } finally {
            setProjectsLoading(false);
        }
    }, []);

    // ========== Fetch Single Project Details ==========
    const fetchProjectDetails = useCallback(async (projectId) => {
        setActiveProjectLoading(true);
        try {
            const response = await api.projects.get(projectId);
            const p = response.data;
            setActiveProject({
                id: p.id,
                title: p.title,
                type: p.type,
                status: p.analysis_state?.status || 'Created',
                domain: p.domain || 'General',
                createdAt: p.created_at,
                ideaText: p.idea_text,
                noveltyRisk: p.analysis_state?.novelty_risk,
                evidenceCount: p.evidence_count || 0,
                files: p.files || [],
                evidence: p.evidence || [],
            });
        } catch (error) {
            console.error('Failed to fetch project details:', error);
        } finally {
            setActiveProjectLoading(false);
        }
    }, []);

    // ========== Create New Project ==========
    const createProject = useCallback(async (projectData) => {
        try {
            const payload = {
                title: projectData.title || 'Untitled Project',
                type: projectData.projectType || 'RESEARCH',
                idea_text: projectData.description || '',
                domain: projectData.domain,
            };
            const response = await api.projects.create(payload);
            const newProject = response.data;
            
            // Refresh projects list
            await fetchProjects();
            
            return newProject;
        } catch (error) {
            console.error('Failed to create project:', error);
            throw error;
        }
    }, [fetchProjects]);

    // ========== Upload File to Project ==========
    const uploadFile = useCallback(async (projectId, file) => {
        try {
            const response = await api.files.upload(projectId, file);
            return response.data;
        } catch (error) {
            console.error('Failed to upload file:', error);
            throw error;
        }
    }, []);

    // ========== Check System Health ==========
    const checkSystemHealth = useCallback(async () => {
        try {
            const response = await api.system.health();
            setSystemStatus(response.data);
            return response.data;
        } catch (error) {
            console.error('Backend health check failed:', error);
            setSystemStatus({ status: 'offline' });
            return null;
        }
    }, []);

    // ========== Initial Data Fetch ==========
    useEffect(() => {
        fetchProjects();
        checkSystemHealth();
    }, [fetchProjects, checkSystemHealth]);

    // ========== Navigation ==========
    const navigateTo = (view) => {
        setCurrentView(view);
        if (view === 'HOME') setActiveProject(null);
    };

    const openProject = async (project) => {
        setCurrentView('DASHBOARD');
        setCreationStage('IDLE');
        await fetchProjectDetails(project.id);
    };

    const startNewProject = (data) => {
        setNewProjectData(prev => ({ ...prev, ...data }));
        setCreationStage('TYPE');
    };

    // ========== Complete Project Creation Flow ==========
    const confirmProjectCreation = async () => {
        try {
            setCreationStage('PROCESSING');
            const newProject = await createProject(newProjectData);
            
            // Set as active project and navigate to dashboard
            await fetchProjectDetails(newProject.id);
            setCreationStage('IDLE');
            setNewProjectData({ title: '', description: '', outcome: '', domain: null, projectType: 'RESEARCH' });
            
            return newProject;
        } catch (error) {
            console.error('Project creation failed:', error);
            setCreationStage('IDLE');
            throw error;
        }
    };

    return (
        <WorkflowContext.Provider value={{
            // View State
            currentView,
            navigateTo,
            
            // Projects
            projects,
            projectsLoading,
            projectsError,
            fetchProjects,
            
            // Active Project
            activeProject,
            activeProjectLoading,
            openProject,
            fetchProjectDetails,
            
            // Creation Flow
            creationStage,
            setCreationStage,
            newProjectData,
            setNewProjectData,
            startNewProject,
            confirmProjectCreation,
            createProject,
            
            // File Operations
            uploadFile,
            
            // System
            systemStatus,
            checkSystemHealth,
            
            // Legacy compatibility
            domain: activeProject?.domain
        }}>
            {children}
        </WorkflowContext.Provider>
    );
};
