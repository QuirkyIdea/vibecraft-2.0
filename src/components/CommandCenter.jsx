/**
 * Inventix AI - Command Center
 * 
 * REFACTORED: Real system status, real project data.
 * All fake metrics removed.
 */
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useWorkflow } from '../context/WorkflowContext';
import api from '../api/endpoints';

const CommandCenter = () => {
    const { activeProject, systemStatus } = useWorkflow();
    const [backendHealth, setBackendHealth] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const checkHealth = async () => {
            try {
                const response = await api.system.health();
                setBackendHealth(response.data);
            } catch (error) {
                setBackendHealth({ status: 'offline' });
            } finally {
                setLoading(false);
            }
        };
        checkHealth();
    }, []);

    const isOnline = backendHealth?.status === 'ok' || backendHealth?.status === 'healthy';

    return (
        <section id="command-center" className="min-h-screen pt-24 px-6 bg-gradient-to-br from-white via-blue-50 to-indigo-50/30">
            <div className="max-w-7xl mx-auto">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="mb-10"
                >
                    <h1 className="text-4xl font-bold mb-2">
                        <span className="text-gray-900">{activeProject?.title || 'Project'}</span> <span className="text-gradient">Control Room</span>
                    </h1>
                    <p className="text-gray-500">
                        System Status: {loading ? (
                            <span className="text-gray-400">Checking...</span>
                        ) : isOnline ? (
                            <span className="text-green-500 font-semibold">● Online</span>
                        ) : (
                            <span className="text-red-500 font-semibold">● Offline</span>
                        )} | Phase: {backendHealth?.phase || '?'} | v{backendHealth?.version || '?'}
                    </p>
                </motion.div>

                {/* Project Summary */}
                {activeProject && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
                        <StatCard 
                            label="Project Type" 
                            value={activeProject.type} 
                            detail={activeProject.domain || 'General'}
                            color="blue"
                        />
                        <StatCard 
                            label="Evidence Items" 
                            value={activeProject.evidenceCount || 0} 
                            detail="Documents analyzed"
                            color="green"
                        />
                        <StatCard 
                            label="Novelty Risk" 
                            value={activeProject.noveltyRisk || 'UNKNOWN'} 
                            detail="Based on similarity"
                            color={getRiskColor(activeProject.noveltyRisk)}
                        />
                        <StatCard 
                            label="Status" 
                            value={activeProject.status || 'Created'} 
                            detail="Current stage"
                            color="purple"
                        />
                    </div>
                )}

                {/* No Project Selected */}
                {!activeProject && (
                    <div className="glass-card p-12 text-center mb-12">
                        <div className="text-6xl mb-4">📋</div>
                        <h3 className="text-xl font-bold text-gray-800 mb-2">No Project Selected</h3>
                        <p className="text-gray-500">Select a project from the sidebar to view its details.</p>
                    </div>
                )}

                {/* Main Dashboard Layout */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Analysis Pipeline */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.4 }}
                        className="lg:col-span-2 glass-card h-[500px] overflow-hidden relative"
                    >
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-xl font-semibold text-gray-800">Analysis Pipeline</h2>
                            <span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-700">Phase 10</span>
                        </div>

                        <div className="space-y-4">
                            {[
                                { step: '1', title: 'Upload Documents', description: 'PDF, DOCX, TXT files containing your research or patent idea', status: 'available' },
                                { step: '2', title: 'Text Extraction', description: 'Real content extracted from your documents', status: 'available' },
                                { step: '3', title: 'Evidence Retrieval', description: 'Search Semantic Scholar & USPTO for related work', status: 'available' },
                                { step: '4', title: 'Similarity Computation', description: 'Cosine similarity between your idea and evidence', status: 'available' },
                                { step: '5', title: 'Novelty Classification', description: 'GREEN/YELLOW/RED risk based on similarity thresholds', status: 'available' },
                                { step: '6', title: 'Draft Optimization', description: 'Localized suggestions to improve your writing', status: 'available' }
                            ].map((item, i) => (
                                <div key={i} className="flex items-start gap-4 p-3 rounded-xl bg-white/40 border border-white/60">
                                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold shrink-0">
                                        {item.step}
                                    </div>
                                    <div className="flex-1">
                                        <div className="flex justify-between items-start">
                                            <h4 className="text-sm font-semibold text-gray-800">{item.title}</h4>
                                            <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700">Available</span>
                                        </div>
                                        <p className="text-xs text-gray-500 mt-1">{item.description}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </motion.div>

                    {/* System Info */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.5 }}
                        className="space-y-8"
                    >
                        {/* Data Sources */}
                        <div className="glass-card">
                            <h3 className="text-lg font-semibold mb-4 text-gray-800">Data Sources</h3>
                            <div className="space-y-3">
                                {[
                                    { name: 'Semantic Scholar', type: 'Research Papers', status: isOnline ? 'Connected' : 'Offline' },
                                    { name: 'USPTO', type: 'Patents', status: isOnline ? 'Connected' : 'Offline' }
                                ].map(source => (
                                    <div key={source.name} className="flex items-center justify-between">
                                        <div>
                                            <span className="text-sm text-gray-700 font-medium">{source.name}</span>
                                            <span className="text-xs text-gray-400 block">{source.type}</span>
                                        </div>
                                        <span className={`text-xs px-2 py-1 rounded-full border ${
                                            source.status === 'Connected' 
                                                ? 'bg-green-100 text-green-700 border-green-200'
                                                : 'bg-red-100 text-red-700 border-red-200'
                                        }`}>{source.status}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Disclaimer */}
                        <div className="glass-card bg-yellow-50/50 border-yellow-200/50">
                            <p className="text-xs text-yellow-800">
                                ⚠️ All analysis is assistive only. Human expert review is required for patent or publication decisions.
                            </p>
                        </div>
                    </motion.div>
                </div>
            </div>
        </section>
    );
};

const StatCard = ({ label, value, detail, color }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        whileHover={{ scale: 1.02 }}
        className="bg-white/60 backdrop-blur-xl border border-white/40 p-6 rounded-2xl shadow-lg"
    >
        <h3 className="text-gray-500 text-sm font-medium mb-2">{label}</h3>
        <div className="flex items-end gap-3">
            <span className={`text-2xl font-bold text-${color}-600`}>{value}</span>
        </div>
        <p className="text-xs text-gray-400 mt-1">{detail}</p>
    </motion.div>
);

const getRiskColor = (risk) => {
    switch (risk) {
        case 'GREEN': return 'green';
        case 'YELLOW': return 'yellow';
        case 'RED': return 'red';
        default: return 'gray';
    }
};

export default CommandCenter;
