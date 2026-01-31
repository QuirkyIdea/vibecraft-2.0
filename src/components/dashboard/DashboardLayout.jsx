import { motion, AnimatePresence } from 'framer-motion';
import { useWorkflow } from '../../context/WorkflowContext';
import MainDashboard from './MainDashboard';
import OnboardingFlow from '../workflow/OnboardingFlow';
import PipelineAnimation from '../workflow/PipelineAnimation';

const DashboardLayout = () => {
    const {
        projects,
        activeProject,
        openProject,
        creationStage,
        startNewProject
    } = useWorkflow();

    // If implementing "New Project", we show the onboarding flow temporarily
    if (creationStage !== 'IDLE') {
        if (creationStage === 'TYPE' || creationStage === 'IDEA' || creationStage === 'UPLOAD') return <OnboardingFlow />;
        if (creationStage === 'SEGREGATION' || creationStage === 'PIPELINE') return <PipelineAnimation />;
    }

    return (
        <div className="min-h-screen bg-gray-50 pt-24 px-6 pb-12">
            <div className="max-w-7xl mx-auto flex gap-8 h-[85vh]">

                {/* Left Sidebar: Project Integration */}
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
                        <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">My Projects</h3>
                        {projects.map((project) => (
                            <motion.div
                                key={project.id}
                                onClick={() => openProject(project)}
                                className={`p-4 rounded-xl cursor-pointer border transition-all ${activeProject?.id === project.id
                                    ? 'bg-white border-blue-400 shadow-md scale-[1.02]'
                                    : 'bg-white/50 border-transparent hover:bg-white hover:border-gray-200'
                                    }`}
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${project.type === 'RESEARCH' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'
                                        }`}>
                                        {project.type}
                                    </span>
                                    <span className="text-xs text-green-600 font-semibold">{project.status}</span>
                                </div>
                                <h4 className="font-bold text-gray-800 text-sm">{project.title}</h4>
                                <p className="text-xs text-gray-500 mt-1">{project.domain} • Last active 2h ago</p>
                            </motion.div>
                        ))}
                    </div>
                </aside>

                {/* Main Content Area */}
                <main className="flex-1 bg-white rounded-3xl border border-gray-200 shadow-sm overflow-hidden relative">
                    {activeProject ? (
                        <div className="h-full overflow-y-auto">
                            {/* We inject the domain context here implicitly via the activeProject state if we updated MainDashboard to use it, 
                                but for now MainDashboard pulls from 'domain' in WorkflowContext. 
                                Ideally, we'd update WorkflowContext to sync activeProject.domain to global domain.
                            */}
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

export default DashboardLayout;
