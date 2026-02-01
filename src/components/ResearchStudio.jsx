/**
 * Inventix AI - Research Studio
 * 
 * REFACTORED: Removed fake marketing stats like "2.4M+ papers".
 * Now shows honest feature descriptions.
 */
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef } from 'react';
import { useWorkflow } from '../context/WorkflowContext';
import api from '../api/endpoints';

const ResearchStudio = () => {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: "-100px" });
    const { activeProject } = useWorkflow();
    
    const [recommendations, setRecommendations] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (activeProject?.id && activeProject.type === 'RESEARCH') {
            fetchRecommendations();
        }
    }, [activeProject?.id]);

    const fetchRecommendations = async () => {
        if (!activeProject?.id) return;
        setLoading(true);
        try {
            const response = await api.venues.get(activeProject.id);
            setRecommendations(response.data);
        } catch (error) {
            console.log('No recommendations yet');
        } finally {
            setLoading(false);
        }
    };

    // Only show for RESEARCH projects
    if (activeProject && activeProject.type !== 'RESEARCH') {
        return null;
    }

    const features = [
        {
            icon: '📖',
            title: 'Literature Search',
            description: 'Search Semantic Scholar for related research papers',
            capability: 'API-integrated'
        },
        {
            icon: '🔎',
            title: 'Gap Detection',
            description: 'Compare your idea against existing research',
            capability: 'Similarity-based'
        },
        {
            icon: '📊',
            title: 'Novelty Analysis',
            description: 'GREEN/YELLOW/RED classification based on overlap',
            capability: 'Deterministic'
        },
        {
            icon: '✍️',
            title: 'Draft Optimization',
            description: 'Get localized suggestions to improve your writing',
            capability: 'Phase 6'
        },
        {
            icon: '🎓',
            title: 'Venue Recommendations',
            description: 'Find conferences and journals for your research',
            capability: 'Phase 7'
        }
    ];

    return (
        <section ref={ref} className="section-container" id="research-studio">
            <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.8 }}
                className="text-center mb-16"
            >
                <h2 className="text-5xl md:text-6xl font-bold text-gradient mb-6">
                    Research Studio
                </h2>
                <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                    AI-assisted research analysis and publication planning
                </p>
            </motion.div>

            {/* Features Grid - Honest descriptions */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
                {features.map((feature, index) => (
                    <motion.div
                        key={feature.title}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={isInView ? { opacity: 1, scale: 1 } : {}}
                        transition={{ delay: index * 0.1, duration: 0.6 }}
                        className="glass-card glow-border group"
                    >
                        <div className="text-5xl mb-4">{feature.icon}</div>
                        <h3 className="text-xl font-bold text-gray-800 mb-3">{feature.title}</h3>
                        <p className="text-gray-600 mb-4 leading-relaxed">{feature.description}</p>
                        <div className="inline-block px-3 py-1 rounded-full bg-gradient-to-r from-ice-100 to-blue-100 text-ice-700 text-sm font-semibold">
                            {feature.capability}
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* Project-specific content */}
            {activeProject && (
                <motion.div
                    className="glass-card glow-border-strong max-w-4xl mx-auto"
                    initial={{ opacity: 0, y: 50 }}
                    animate={isInView ? { opacity: 1, y: 0 } : {}}
                    transition={{ delay: 0.6, duration: 0.8 }}
                >
                    <h3 className="text-3xl font-bold text-center text-gradient mb-8">
                        Research Analysis
                    </h3>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        {/* Project Status */}
                        <div className="space-y-4">
                            <h4 className="text-xl font-bold text-gray-800">Project Status</h4>
                            
                            <div className="p-4 rounded-xl bg-white/50 border border-gray-200">
                                <div className="text-sm text-gray-500">Novelty Risk</div>
                                <div className={`text-2xl font-bold ${getRiskColor(activeProject.noveltyRisk)}`}>
                                    {activeProject.noveltyRisk || 'UNKNOWN'}
                                </div>
                            </div>
                            
                            <div className="p-4 rounded-xl bg-white/50 border border-gray-200">
                                <div className="text-sm text-gray-500">Evidence Items</div>
                                <div className="text-2xl font-bold text-gray-800">{activeProject.evidenceCount || 0}</div>
                            </div>
                            
                            <div className="p-4 rounded-xl bg-white/50 border border-gray-200">
                                <div className="text-sm text-gray-500">Domain</div>
                                <div className="text-xl font-bold text-gray-800">{activeProject.domain || 'General'}</div>
                            </div>
                        </div>

                        {/* Venue Recommendations */}
                        <div className="space-y-4">
                            <h4 className="text-xl font-bold text-gray-800">Venue Recommendations</h4>
                            
                            {loading ? (
                                <div className="text-center py-8">
                                    <motion.div
                                        animate={{ rotate: 360 }}
                                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                        className="text-3xl inline-block"
                                    >
                                        ⚙️
                                    </motion.div>
                                </div>
                            ) : recommendations?.recommendations?.length > 0 ? (
                                <div className="space-y-3 max-h-64 overflow-y-auto">
                                    {recommendations.recommendations.slice(0, 5).map((venue, i) => (
                                        <div key={i} className="p-4 rounded-xl bg-white/50 border border-gray-200">
                                            <div className="font-semibold text-gray-800">{venue.name}</div>
                                            <div className="text-xs text-gray-500">{venue.type} • {venue.field}</div>
                                            <div className="text-xs text-blue-600 mt-1">Score: {venue.match_score?.toFixed(2) || 'N/A'}</div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-8 bg-gray-50 rounded-xl">
                                    <div className="text-4xl mb-2">🎓</div>
                                    <p className="text-gray-500 text-sm">No recommendations yet</p>
                                    <p className="text-xs text-gray-400 mt-1">Upload evidence and run analysis first</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Disclaimer */}
                    <div className="mt-8 p-4 rounded-xl bg-yellow-50 border border-yellow-200">
                        <p className="text-xs text-yellow-800 text-center">
                            ⚠️ All analysis is assistive only. Venue recommendations are suggestions based on similarity matching. 
                            Always verify submission requirements directly with the venue.
                        </p>
                    </div>
                </motion.div>
            )}

            {/* No Project Selected */}
            {!activeProject && (
                <div className="glass-card max-w-2xl mx-auto text-center py-12">
                    <div className="text-6xl mb-4">🔬</div>
                    <h3 className="text-xl font-bold text-gray-800 mb-2">Select a Research Project</h3>
                    <p className="text-gray-500">Create or select a RESEARCH type project to use the Research Studio.</p>
                </div>
            )}
        </section>
    );
};

const getRiskColor = (risk) => {
    switch (risk) {
        case 'GREEN': return 'text-green-600';
        case 'YELLOW': return 'text-yellow-600';
        case 'RED': return 'text-red-600';
        default: return 'text-gray-500';
    }
};

export default ResearchStudio;
