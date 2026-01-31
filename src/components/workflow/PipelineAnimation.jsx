import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useState } from 'react';
import { useWorkflow } from '../../context/WorkflowContext';
import NeuralBackground from '../home/NeuralBackground';

const PipelineAnimation = () => {
    const { confirmProjectCreation } = useWorkflow();
    const [activeNode, setActiveNode] = useState(0);

    const nodes = [
        { id: 'brain', label: 'AI Brain Core', icon: '🧠', color: 'blue' },
        { id: 'agents', label: 'Multi-Agent Swarm', icon: '🤖', color: 'purple' },
        { id: 'graph', label: 'Knowledge Graph', icon: '🕸️', color: 'emerald' },
        { id: 'research', label: 'Research Engine', icon: '🔬', color: 'cyan' },
        { id: 'patent', label: 'Patent Risk Engine', icon: '⚖️', color: 'orange' },
        { id: 'output', label: 'Pipeline Generated', icon: '✅', color: 'green' }
    ];

    useEffect(() => {
        const interval = setInterval(() => {
            setActiveNode(prev => {
                if (prev >= nodes.length - 1) {
                    clearInterval(interval);
                    setTimeout(confirmProjectCreation, 1000); // Wait a bit then finish
                    return prev;
                }
                return prev + 1;
            });
        }, 800); // Switch node every 800ms

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="fixed inset-0 z-50 bg-white/90 backdrop-blur-xl flex items-center justify-center">
            <NeuralBackground />
            <div className="max-w-5xl w-full p-8 relative z-10 glass-card">
                <h2 className="text-4xl font-bold text-center mb-20 text-gray-900 tracking-tight">
                    Constructing Intelligence Pipeline...
                </h2>

                {/* Connection Line Background */}
                <div className="absolute top-1/2 left-0 w-full h-[2px] bg-gray-100 -translate-y-1/2" />

                {/* Active Progress Line */}
                <motion.div
                    className="absolute top-1/2 left-0 h-1 bg-gradient-to-r from-blue-400 to-purple-600 -translate-y-1/2"
                    initial={{ width: 0 }}
                    animate={{ width: `${(activeNode / (nodes.length - 1)) * 100}%` }}
                    transition={{ duration: 0.5 }}
                />

                <div className="relative flex justify-between items-center z-10">
                    {nodes.map((node, index) => {
                        const isActive = index === activeNode;
                        const isCompleted = index < activeNode;

                        return (
                            <div key={node.id} className="flex flex-col items-center gap-4">
                                <motion.div
                                    className={`w-20 h-20 rounded-2xl flex items-center justify-center text-4xl border-2 transition-all duration-300
                                        ${isActive || isCompleted
                                            ? `bg-white border-${node.color}-500 shadow-xl shadow-${node.color}-500/20 scale-110`
                                            : 'bg-gray-50 border-gray-200 grayscale opacity-50'
                                        }`}
                                    initial={{ scale: 0.8 }}
                                    animate={{ scale: isActive ? 1.2 : isCompleted ? 1 : 0.8 }}
                                >
                                    {node.icon}
                                </motion.div>

                                <motion.div
                                    className="text-center"
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{
                                        opacity: isActive || isCompleted ? 1 : 0,
                                        y: isActive || isCompleted ? 0 : 10
                                    }}
                                >
                                    <p className={`font-bold text-sm ${isActive ? `text-${node.color}-600` : 'text-gray-800'}`}>
                                        {node.label}
                                    </p>
                                    {isActive && (
                                        <motion.span
                                            className="text-xs text-gray-400"
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                        >
                                            Initializing...
                                        </motion.span>
                                    )}
                                    {isCompleted && (
                                        <span className="text-xs text-green-500 font-mono">OK</span>
                                    )}
                                </motion.div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default PipelineAnimation;
