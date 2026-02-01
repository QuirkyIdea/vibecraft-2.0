/**
 * Inventix AI - Patent Studio
 * 
 * REFACTORED: All fake stats removed.
 * Now displays real claim data from API or shows "Not Generated" states.
 */
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef } from 'react';
import { useWorkflow } from '../context/WorkflowContext';
import api from '../api/endpoints';

const PatentStudio = () => {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: "-100px" });
    const { activeProject } = useWorkflow();
    
    const [claims, setClaims] = useState([]);
    const [claimsLoading, setClaimsLoading] = useState(false);
    const [noveltyData, setNoveltyData] = useState(null);

    // Fetch claims when project changes
    useEffect(() => {
        if (activeProject?.id && activeProject.type === 'PATENT') {
            fetchClaims();
            fetchNovelty();
        }
    }, [activeProject?.id]);

    const fetchClaims = async () => {
        if (!activeProject?.id) return;
        setClaimsLoading(true);
        try {
            const response = await api.claims.list(activeProject.id);
            setClaims(response.data.claims || []);
        } catch (error) {
            console.log('No claims generated yet');
            setClaims([]);
        } finally {
            setClaimsLoading(false);
        }
    };

    const fetchNovelty = async () => {
        if (!activeProject?.id) return;
        try {
            const response = await api.similarity.getNovelty(activeProject.id);
            setNoveltyData(response.data);
        } catch (error) {
            console.log('No novelty data available');
        }
    };

    const generateClaims = async () => {
        if (!activeProject?.id) return;
        setClaimsLoading(true);
        try {
            await api.claims.generate(activeProject.id);
            await fetchClaims();
        } catch (error) {
            console.error('Claim generation failed:', error);
            alert(error.response?.data?.detail || 'Claim generation failed. Please try again.');
        } finally {
            setClaimsLoading(false);
        }
    };

    // Only show for PATENT projects
    if (activeProject && activeProject.type !== 'PATENT') {
        return null;
    }

    return (
        <section ref={ref} className="section-container" id="patent-studio">
            <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.8 }}
                className="text-center mb-16"
            >
                <h2 className="text-5xl md:text-6xl font-bold text-gradient mb-6">
                    Patent Studio
                </h2>
                <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                    AI-assisted patent claim structuring and analysis
                </p>
            </motion.div>

            {/* Features Grid - Honest descriptions */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
                {[
                    {
                        icon: '🔍',
                        title: 'Prior Art Search',
                        description: 'Search USPTO and Semantic Scholar for related work',
                        capability: 'Evidence-based'
                    },
                    {
                        icon: '⚖️',
                        title: 'Similarity Analysis',
                        description: 'Compute semantic similarity against evidence',
                        capability: 'Deterministic'
                    },
                    {
                        icon: '📊',
                        title: 'Novelty Classification',
                        description: 'GREEN/YELLOW/RED based on similarity scores',
                        capability: 'Threshold-based'
                    },
                    {
                        icon: '📝',
                        title: 'Claim Drafting',
                        description: 'Generate structured patent claim suggestions',
                        capability: 'Conceptual only'
                    },
                    {
                        icon: '🔗',
                        title: 'Dependency Graph',
                        description: 'Visualize claim relationships',
                        capability: 'Phase 8'
                    }
                ].map((feature, index) => (
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

            {/* Real Claims Section */}
            {activeProject && (
                <motion.div
                    className="glass-card glow-border-strong max-w-4xl mx-auto"
                    initial={{ opacity: 0, y: 50 }}
                    animate={isInView ? { opacity: 1, y: 0 } : {}}
                    transition={{ delay: 0.6, duration: 0.8 }}
                >
                    <h3 className="text-3xl font-bold text-center text-gradient mb-8">
                        Patent Claims
                    </h3>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                        {/* Novelty Status */}
                        <div className="text-center">
                            <div className="text-sm text-gray-600 mb-2">Novelty Risk Level</div>
                            <NoveltyDisplay risk={noveltyData?.novelty_risk || activeProject.noveltyRisk} />
                            
                            <div className="mt-8 space-y-4">
                                <div className="p-4 rounded-xl bg-white/50 border border-gray-200">
                                    <div className="text-sm text-gray-500">Evidence Items</div>
                                    <div className="text-2xl font-bold text-gray-800">{activeProject.evidenceCount || 0}</div>
                                </div>
                                <div className="p-4 rounded-xl bg-white/50 border border-gray-200">
                                    <div className="text-sm text-gray-500">Claims Generated</div>
                                    <div className="text-2xl font-bold text-gray-800">{claims.length}</div>
                                </div>
                            </div>
                        </div>

                        {/* Claims List */}
                        <div className="space-y-4">
                            <h4 className="text-xl font-bold text-gray-800 mb-4">Generated Claims</h4>

                            {claimsLoading ? (
                                <div className="text-center py-8">
                                    <motion.div
                                        animate={{ rotate: 360 }}
                                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                        className="text-3xl inline-block"
                                    >
                                        ⚙️
                                    </motion.div>
                                    <p className="text-gray-500 mt-2">Loading claims...</p>
                                </div>
                            ) : claims.length > 0 ? (
                                <div className="space-y-3 max-h-64 overflow-y-auto">
                                    {claims.map((claim, i) => (
                                        <motion.div
                                            key={claim.id || i}
                                            className="p-4 rounded-xl bg-white/50 border border-gray-200"
                                            initial={{ opacity: 0, x: 20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: i * 0.1 }}
                                        >
                                            <div className="flex items-center gap-2 mb-2">
                                                <span className={`text-xs px-2 py-1 rounded-full ${
                                                    claim.claim_type === 'INDEPENDENT' 
                                                        ? 'bg-blue-100 text-blue-700'
                                                        : 'bg-gray-100 text-gray-600'
                                                }`}>
                                                    {claim.claim_type}
                                                </span>
                                                <span className="text-xs text-gray-400">Claim {claim.claim_number || i + 1}</span>
                                            </div>
                                            <p className="text-sm text-gray-700 line-clamp-2">{claim.claim_text}</p>
                                        </motion.div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-8 bg-gray-50 rounded-xl">
                                    <div className="text-4xl mb-2">📄</div>
                                    <p className="text-gray-500">No claims generated yet</p>
                                    <motion.button
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                        onClick={generateClaims}
                                        className="btn-primary mt-4"
                                        disabled={claimsLoading}
                                    >
                                        Generate Claims
                                    </motion.button>
                                </div>
                            )}

                            {claims.length > 0 && (
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={generateClaims}
                                    className="w-full btn-primary mt-4"
                                    disabled={claimsLoading}
                                >
                                    Regenerate Claims
                                </motion.button>
                            )}
                        </div>
                    </div>

                    {/* Disclaimer */}
                    <div className="mt-8 p-4 rounded-xl bg-yellow-50 border border-yellow-200">
                        <p className="text-xs text-yellow-800 text-center">
                            ⚠️ <strong>CONCEPTUAL DRAFTS ONLY</strong> - These are AI-generated suggestions for educational purposes. 
                            They are NOT legal advice. Consult a registered patent attorney before filing.
                        </p>
                    </div>
                </motion.div>
            )}

            {/* No Project Selected */}
            {!activeProject && (
                <div className="glass-card max-w-2xl mx-auto text-center py-12">
                    <div className="text-6xl mb-4">📄</div>
                    <h3 className="text-xl font-bold text-gray-800 mb-2">Select a Patent Project</h3>
                    <p className="text-gray-500">Create or select a PATENT type project to use the Patent Studio.</p>
                </div>
            )}
        </section>
    );
};

const NoveltyDisplay = ({ risk }) => {
    const colors = {
        GREEN: { bg: 'bg-green-100', text: 'text-green-600', label: 'Low Risk' },
        YELLOW: { bg: 'bg-yellow-100', text: 'text-yellow-600', label: 'Medium Risk' },
        RED: { bg: 'bg-red-100', text: 'text-red-600', label: 'High Risk' },
        UNKNOWN: { bg: 'bg-gray-100', text: 'text-gray-500', label: 'Not Analyzed' }
    };
    
    const config = colors[risk] || colors.UNKNOWN;
    
    return (
        <div className={`inline-block px-8 py-6 rounded-2xl ${config.bg}`}>
            <div className={`text-4xl font-bold ${config.text}`}>{risk || 'UNKNOWN'}</div>
            <div className="text-sm text-gray-600 mt-1">{config.label}</div>
        </div>
    );
};

export default PatentStudio;
