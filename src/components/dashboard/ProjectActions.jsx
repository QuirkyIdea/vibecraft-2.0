/**
 * Inventix AI - Project Actions
 * 
 * Provides buttons to trigger the analysis pipeline:
 * Extract Text → Retrieve Evidence → Compute Similarity → Generate Analysis
 */
import { useState } from 'react';
import { motion } from 'framer-motion';
import { useWorkflow } from '../../context/WorkflowContext';
import api from '../../api/endpoints';

const ProjectActions = () => {
    const { activeProject, fetchProjectDetails } = useWorkflow();
    const [loading, setLoading] = useState({});
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    if (!activeProject) return null;

    const runAction = async (actionName, apiCall) => {
        setLoading(prev => ({ ...prev, [actionName]: true }));
        setError(null);
        setSuccess(null);
        
        try {
            await apiCall();
            setSuccess(`${actionName} completed successfully!`);
            // Refresh project details
            await fetchProjectDetails(activeProject.id);
        } catch (err) {
            console.error(`${actionName} failed:`, err);
            setError(err.response?.data?.detail || `${actionName} failed. Please try again.`);
        } finally {
            setLoading(prev => ({ ...prev, [actionName]: false }));
        }
    };

    const actions = [
        {
            name: 'Extract Text',
            icon: '📄',
            description: 'Extract text from uploaded documents',
            action: () => api.extraction.extract(activeProject.id),
            phase: 2
        },
        {
            name: 'Find Papers',
            icon: '📚',
            description: 'Search Semantic Scholar for related research',
            action: () => api.evidence.retrievePapers(activeProject.id, { 
                query: activeProject.ideaText?.substring(0, 200) || activeProject.title,
                max_results: 10 
            }),
            phase: 3
        },
        {
            name: 'Find Patents',
            icon: '📜',
            description: 'Search USPTO for similar patents',
            action: () => api.evidence.retrievePatents(activeProject.id, { 
                query: activeProject.ideaText?.substring(0, 200) || activeProject.title,
                max_results: 10 
            }),
            phase: 3
        },
        {
            name: 'Generate Embeddings',
            icon: '🧠',
            description: 'Create vector embeddings for similarity',
            action: () => api.similarity.generateEmbeddings(activeProject.id),
            phase: 4
        },
        {
            name: 'Compute Similarity',
            icon: '📊',
            description: 'Calculate similarity to evidence',
            action: () => api.similarity.compute(activeProject.id),
            phase: 4
        },
        {
            name: 'Generate Analysis',
            icon: '🔍',
            description: 'Create comparative analysis report',
            action: () => api.analysis.generate(activeProject.id, 5),
            phase: 5
        }
    ];

    const runFullPipeline = async () => {
        setError(null);
        setSuccess(null);
        
        const steps = [
            { name: 'Extract Text', action: () => api.extraction.extract(activeProject.id) },
            { name: 'Find Papers', action: () => api.evidence.retrievePapers(activeProject.id, { 
                query: activeProject.ideaText?.substring(0, 200) || activeProject.title, 
                max_results: 10 
            })},
            { name: 'Generate Embeddings', action: () => api.similarity.generateEmbeddings(activeProject.id) },
            { name: 'Compute Similarity', action: () => api.similarity.compute(activeProject.id) },
            { name: 'Generate Analysis', action: () => api.analysis.generate(activeProject.id, 5) }
        ];
        
        for (const step of steps) {
            try {
                setLoading(prev => ({ ...prev, [step.name]: true }));
                await step.action();
                setLoading(prev => ({ ...prev, [step.name]: false }));
            } catch (err) {
                setLoading({});
                setError(`Pipeline failed at "${step.name}": ${err.response?.data?.detail || err.message}`);
                return;
            }
        }
        
        setSuccess('Full analysis pipeline completed!');
        await fetchProjectDetails(activeProject.id);
    };

    return (
        <div className="glass-card p-6 mb-6">
            <h3 className="text-lg font-bold text-gray-800 mb-4">🔬 Analysis Pipeline</h3>
            
            {error && (
                <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
                    ⚠️ {error}
                </div>
            )}
            
            {success && (
                <div className="mb-4 p-3 rounded-lg bg-green-50 border border-green-200 text-green-700 text-sm">
                    ✓ {success}
                </div>
            )}

            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {actions.map((action) => (
                    <motion.button
                        key={action.name}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => runAction(action.name, action.action)}
                        disabled={loading[action.name]}
                        className={`p-4 rounded-xl border text-left transition-all ${
                            loading[action.name]
                                ? 'bg-gray-100 border-gray-200 cursor-wait'
                                : 'bg-white border-gray-200 hover:border-blue-400 hover:bg-blue-50/30'
                        }`}
                    >
                        <div className="flex items-center gap-2 mb-1">
                            <span className="text-xl">{action.icon}</span>
                            {loading[action.name] && (
                                <motion.span
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                    className="text-sm"
                                >
                                    ⚙️
                                </motion.span>
                            )}
                        </div>
                        <div className="text-sm font-semibold text-gray-800">{action.name}</div>
                        <div className="text-xs text-gray-500">{action.description}</div>
                        <div className="text-xs text-blue-500 mt-1">Phase {action.phase}</div>
                    </motion.button>
                ))}
            </div>

            {/* Run Full Pipeline Button */}
            <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={runFullPipeline}
                disabled={Object.values(loading).some(Boolean)}
                className="w-full mt-4 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 text-white font-bold shadow-lg shadow-blue-500/20 disabled:opacity-50 disabled:cursor-wait"
            >
                🚀 Run Full Analysis Pipeline
            </motion.button>
        </div>
    );
};

export default ProjectActions;
