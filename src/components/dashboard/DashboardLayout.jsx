/**
 * Inventix AI - Dashboard Layout
 * 
 * REFACTORED: Real project data from API, proper loading states.
 */
import { motion, AnimatePresence } from 'framer-motion';
import { useWorkflow } from '../../context/WorkflowContext';
import MainDashboard from './MainDashboard';
import OnboardingFlow from '../workflow/OnboardingFlow';

const DashboardLayout = () => {
    const {
        projects,
        projectsLoading,
        projectsError,
        activeProject,
        activeProjectLoading,
        openProject,
        creationStage,
        startNewProject,
        fetchProjects
    } = useWorkflow();

    // Show onboarding flow when in creation mode
    if (creationStage !== 'IDLE') {
        return <OnboardingFlow />;
    }

    return (
        <div className="min-h-screen bg-gray-50 pt-24 px-6 pb-12">
            <div className="max-w-7xl mx-auto flex gap-8 h-[85vh]">

                {/* Left Sidebar: Project List */}
                <aside className="w-80 flex flex-col gap-6">
                    {/* New Project Button */}
                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => startNewProject({ title: '', description: '', domain: null })}
                        className="w-full py-4 rounded-2xl bg-gradient-to-r from-blue-600 to-cyan-500 text-white font-bold shadow-lg shadow-blue-500/20 flex items-center justify-center gap-2"
                    >
                        <span>+</span> New Project
                    </motion.button>

                    {/* Project List */}
                    <div className="flex-1 overflow-y-auto glass-panel p-4 space-y-3">
                        <div className="flex justify-between items-center mb-2">
                            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider">My Projects</h3>
                            <button 
                                onClick={fetchProjects}
                                className="text-xs text-blue-500 hover:text-blue-700"
                            >
                                ↻ Refresh
                            </button>
                        </div>

                        {/* Loading State */}
                        {projectsLoading && (
                            <div className="flex items-center justify-center py-8">
                                <motion.div
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                    className="text-2xl"
                                >
                                    ⚙️
                                </motion.div>
                                <span className="ml-2 text-gray-500 text-sm">Loading...</span>
                            </div>
                        )}

                        {/* Error State */}
                        {projectsError && (
                            <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
                                ⚠️ {projectsError}
                                <button
                                    onClick={fetchProjects}
                                    className="block mt-2 text-xs underline"
                                >
                                    Try Again
                                </button>
                            </div>
                        )}

                        {/* Empty State */}
                        {!projectsLoading && !projectsError && projects.length === 0 && (
                            <div className="text-center py-8 text-gray-400">
                                <div className="text-4xl mb-2">📂</div>
                                <p className="text-sm">No projects yet.</p>
                                <p className="text-xs">Click "New Project" to get started.</p>
                            </div>
                        )}

                        {/* Project Cards */}
                        {!projectsLoading && projects.map((project) => (
                            <motion.div
                                key={project.id}
                                onClick={() => openProject(project)}
                                whileHover={{ scale: 1.02 }}
                                className={`p-4 rounded-xl cursor-pointer border transition-all ${activeProject?.id === project.id
                                    ? 'bg-white border-blue-400 shadow-md'
                                    : 'bg-white/50 border-transparent hover:bg-white hover:border-gray-200'
                                    }`}
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                                        project.type === 'RESEARCH' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'
                                    }`}>
                                        {project.type}
                                    </span>
                                    {project.noveltyRisk && (
                                        <NoveltyBadge risk={project.noveltyRisk} />
                                    )}
                                </div>
                                <h4 className="font-bold text-gray-800 text-sm">{project.title}</h4>
                                <p className="text-xs text-gray-500 mt-1">
                                    {project.domain || 'General'} • {project.evidenceCount || 0} evidence
                                </p>
                            </motion.div>
                        ))}
                    </div>
                </aside>

                {/* Main Content Area */}
                <main className="flex-1 bg-white rounded-3xl border border-gray-200 shadow-sm overflow-hidden relative">
                    {activeProjectLoading ? (
                        <div className="h-full flex items-center justify-center">
                            <motion.div
                                animate={{ rotate: 360 }}
                                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                className="text-4xl"
                            >
                                ⚙️
                            </motion.div>
                        </div>
                    ) : activeProject ? (
                        <div className="h-full overflow-y-auto">
                            <MainDashboard />
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-center p-8 bg-gray-50/50">
                            <div className="w-24 h-24 bg-white rounded-full flex items-center justify-center shadow-sm mb-6 text-4xl grayscale opacity-50">
                                🚀
                            </div>
                            <h2 className="text-2xl font-bold text-gray-800 mb-2">Select a Project</h2>
                            <p className="text-gray-500 max-w-md">
                                Choose a project from the left sidebar to view its intelligence dashboard, or create a new one to start the AI pipeline.
                            </p>
                        </div>
                    )}
                </main>
            </div>
        </div>
    );
};

// Novelty Risk Badge Component
const NoveltyBadge = ({ risk }) => {
    const colors = {
        GREEN: 'bg-green-100 text-green-700',
        YELLOW: 'bg-yellow-100 text-yellow-700',
        RED: 'bg-red-100 text-red-700',
        UNKNOWN: 'bg-gray-100 text-gray-500'
    };
    
    return (
        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${colors[risk] || colors.UNKNOWN}`}>
            {risk || 'UNKNOWN'}
        </span>
    );
};

export default DashboardLayout;
