import { createContext, useContext, useState } from 'react';

const WorkflowContext = createContext();

export const useWorkflow = () => useContext(WorkflowContext);

export const WorkflowProvider = ({ children }) => {
    // Views: 'HOME', 'DASHBOARD'
    const [currentView, setCurrentView] = useState('HOME');

    // Projects (Mock Data)
    const [projects, setProjects] = useState([
        { id: 1, title: 'Neural Drone Nav', type: 'RESEARCH', status: 'In Progress', domain: 'AI' }
    ]);

    // Active Project State (null = Project List View)
    const [activeProject, setActiveProject] = useState(null);

    // New Project Creation Flow State
    // Stages: 'IDLE', 'TYPE', 'IDEA', 'UPLOAD', 'SEGREGATION', 'PIPELINE', 'ACTIVE'
    const [creationStage, setCreationStage] = useState('IDLE');
    const [newProjectData, setNewProjectData] = useState({ title: '', description: '', outcome: '', domain: null, projectType: 'RESEARCH' });

    const navigateTo = (view) => {
        setCurrentView(view);
        if (view === 'HOME') setActiveProject(null);
    };

    const openProject = (project) => {
        setActiveProject(project);
        setCurrentView('DASHBOARD');
        setCreationStage('IDLE'); // Ensure we aren't in creation flow
    };

    const startNewProject = (data) => {
        setNewProjectData(prev => ({ ...prev, ...data }));
        setCreationStage('TYPE');
    };

    const confirmProjectCreation = () => {
        const newProj = {
            id: Date.now(),
            title: newProjectData.title,
            type: newProjectData.projectType,
            status: 'Initializing',
            domain: newProjectData.domain
        };
        setProjects([...projects, newProj]);
        setActiveProject(newProj);
        setCreationStage('IDLE'); // Reset to IDLE
    };

    return (
        <WorkflowContext.Provider value={{
            currentView,
            navigateTo,
            projects,
            activeProject,
            openProject,
            creationStage,
            setCreationStage,
            newProjectData,
            setNewProjectData,
            startNewProject,
            confirmProjectCreation,
            domain: activeProject?.domain
        }}>
            {children}
        </WorkflowContext.Provider>
    );
};
