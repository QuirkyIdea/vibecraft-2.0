/**
 * Inventix AI - Evidence Panel
 * 
 * Displays retrieved papers and patents with similarity scores.
 */
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useWorkflow } from '../../context/WorkflowContext';
import api from '../../api/endpoints';

const EvidencePanel = () => {
    const { activeProject } = useWorkflow();
    const [evidence, setEvidence] = useState([]);
    const [similarities, setSimilarities] = useState([]);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('evidence');

    useEffect(() => {
        if (activeProject?.id) {
            fetchEvidence();
            fetchSimilarities();
        }
    }, [activeProject?.id]);

    const fetchEvidence = async () => {
        if (!activeProject?.id) return;
        setLoading(true);
        try {
            const response = await api.evidence.list(activeProject.id);
            setEvidence(response.data.evidence || response.data || []);
        } catch (error) {
            console.log('No evidence yet');
            setEvidence([]);
        } finally {
            setLoading(false);
        }
    };

    const fetchSimilarities = async () => {
        if (!activeProject?.id) return;
        try {
            const response = await api.similarity.list(activeProject.id);
            setSimilarities(response.data.scores || response.data || []);
        } catch (error) {
            console.log('No similarity scores yet');
            setSimilarities([]);
        }
    };

    if (!activeProject) return null;

    return (
        <div className="glass-card p-6 mb-6">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold text-gray-800">Evidence & Analysis</h3>
                <div className="flex gap-2">
                    <button
                        onClick={() => setActiveTab('evidence')}
                        className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                            activeTab === 'evidence' 
                                ? 'bg-blue-100 text-blue-700' 
                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}
                    >
                        Evidence ({evidence.length})
                    </button>
                    <button
                        onClick={() => setActiveTab('similarity')}
                        className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                            activeTab === 'similarity' 
                                ? 'bg-blue-100 text-blue-700' 
                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}
                    >
                        Similarity ({similarities.length})
                    </button>
                </div>
            </div>

            {loading ? (
                <div className="flex items-center justify-center py-8">
                    <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="text-2xl"
                    >
                        ⚙️
                    </motion.div>
                </div>
            ) : activeTab === 'evidence' ? (
                <EvidenceList evidence={evidence} />
            ) : (
                <SimilarityList similarities={similarities} />
            )}
        </div>
    );
};

const EvidenceList = ({ evidence }) => {
    if (evidence.length === 0) {
        return (
            <div className="text-center py-8 bg-gray-50 rounded-xl">
                <div className="text-4xl mb-2">📚</div>
                <p className="text-gray-500 text-sm">No evidence retrieved yet</p>
                <p className="text-xs text-gray-400 mt-1">Use "Find Papers" or "Find Patents" to retrieve evidence</p>
            </div>
        );
    }

    return (
        <div className="space-y-3 max-h-80 overflow-y-auto">
            {evidence.map((item, index) => (
                <motion.div
                    key={item.id || index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="p-4 rounded-xl bg-white border border-gray-200 hover:border-blue-300 transition-colors"
                >
                    <div className="flex items-start justify-between gap-2">
                        <div className="flex-1">
                            <span className={`text-xs px-2 py-0.5 rounded-full mr-2 ${
                                item.source_type === 'paper' 
                                    ? 'bg-blue-100 text-blue-700'
                                    : 'bg-purple-100 text-purple-700'
                            }`}>
                                {item.source_type === 'paper' ? '📄 Paper' : '📜 Patent'}
                            </span>
                            <h4 className="text-sm font-semibold text-gray-800 mt-2 line-clamp-2">
                                {item.title}
                            </h4>
                            {item.authors && (
                                <p className="text-xs text-gray-500 mt-1">
                                    {item.authors}
                                </p>
                            )}
                            {item.abstract && (
                                <p className="text-xs text-gray-600 mt-2 line-clamp-3">
                                    {item.abstract}
                                </p>
                            )}
                        </div>
                    </div>
                    {item.url && (
                        <a 
                            href={item.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-xs text-blue-600 hover:underline mt-2 inline-block"
                        >
                            View Source →
                        </a>
                    )}
                </motion.div>
            ))}
        </div>
    );
};

const SimilarityList = ({ similarities }) => {
    if (similarities.length === 0) {
        return (
            <div className="text-center py-8 bg-gray-50 rounded-xl">
                <div className="text-4xl mb-2">📊</div>
                <p className="text-gray-500 text-sm">No similarity scores yet</p>
                <p className="text-xs text-gray-400 mt-1">Run "Generate Embeddings" then "Compute Similarity"</p>
            </div>
        );
    }

    return (
        <div className="space-y-2 max-h-80 overflow-y-auto">
            {similarities.sort((a, b) => b.similarity_score - a.similarity_score).map((item, index) => (
                <motion.div
                    key={item.id || index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.03 }}
                    className="p-3 rounded-lg bg-white border border-gray-200 flex items-center gap-3"
                >
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center text-white font-bold text-sm ${
                        item.similarity_score >= 0.8 ? 'bg-red-500' :
                        item.similarity_score >= 0.5 ? 'bg-yellow-500' :
                        'bg-green-500'
                    }`}>
                        {(item.similarity_score * 100).toFixed(0)}%
                    </div>
                    <div className="flex-1 min-w-0">
                        <h4 className="text-sm font-medium text-gray-800 truncate">
                            {item.evidence_title || `Evidence #${index + 1}`}
                        </h4>
                        <p className="text-xs text-gray-500">
                            {item.source_type === 'paper' ? '📄 Paper' : '📜 Patent'}
                        </p>
                    </div>
                </motion.div>
            ))}
        </div>
    );
};

export default EvidencePanel;
