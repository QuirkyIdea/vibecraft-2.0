import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef, useState } from 'react';

const IntelligenceEngine = () => {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: "-100px" });
    const [scanning, setScanning] = useState(false);

    return (
        <section ref={ref} className="section-container" id="intelligence">
            <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.8 }}
                className="text-center mb-16"
            >
                <h2 className="text-5xl md:text-6xl font-bold text-gradient mb-6">
                    Live Intelligence Engine
                </h2>
                <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                    Real-time novelty detection and knowledge graph exploration
                </p>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                {/* Radar Scanner */}
                <motion.div
                    className="glass-card glow-border"
                    initial={{ opacity: 0, x: -50 }}
                    animate={isInView ? { opacity: 1, x: 0 } : {}}
                    transition={{ delay: 0.2, duration: 0.8 }}
                >
                    <h3 className="text-2xl font-bold text-gray-800 mb-6">Novelty Radar Scanner</h3>

                    <div className="relative aspect-square bg-gradient-to-br from-ice-100 to-blue-100 rounded-xl overflow-hidden">
                        {/* Radar circles */}
                        {[1, 2, 3, 4].map((i) => (
                            <motion.div
                                key={i}
                                className="absolute top-1/2 left-1/2 border-2 border-ice-400/30 rounded-full"
                                style={{
                                    width: `${i * 25}%`,
                                    height: `${i * 25}%`,
                                    transform: 'translate(-50%, -50%)'
                                }}
                                animate={{
                                    scale: [1, 1.05, 1],
                                    opacity: [0.3, 0.6, 0.3]
                                }}
                                transition={{
                                    duration: 3,
                                    repeat: Infinity,
                                    delay: i * 0.2
                                }}
                            />
                        ))}

                        {/* Scanning beam */}
                        <motion.div
                            className="absolute top-1/2 left-1/2 w-1/2 h-1 origin-left"
                            style={{
                                background: 'linear-gradient(90deg, rgba(96,165,250,0.8), transparent)',
                                transformOrigin: 'left center'
                            }}
                            animate={{
                                rotate: [0, 360]
                            }}
                            transition={{
                                duration: 4,
                                repeat: Infinity,
                                ease: "linear"
                            }}
                        />

                        {/* Detection points */}
                        {[...Array(8)].map((_, i) => (
                            <motion.div
                                key={i}
                                className="absolute w-3 h-3 rounded-full bg-ice-500 glow-border-strong"
                                style={{
                                    left: `${20 + Math.random() * 60}%`,
                                    top: `${20 + Math.random() * 60}%`
                                }}
                                animate={{
                                    scale: [0, 1, 1, 0],
                                    opacity: [0, 1, 1, 0]
                                }}
                                transition={{
                                    duration: 3,
                                    repeat: Infinity,
                                    delay: i * 0.3
                                }}
                            />
                        ))}

                        {/* Center indicator */}
                        <div className="absolute top-1/2 left-1/2 w-4 h-4 rounded-full bg-blue-600 -translate-x-1/2 -translate-y-1/2 glow-border-strong" />
                    </div>

                    <div className="mt-6 space-y-3">
                        <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-600">Similarity Engine</span>
                            <span className="font-semibold text-green-600">Ready</span>
                        </div>
                        <div className="h-2 bg-green-100 rounded-full overflow-hidden">
                            <motion.div
                                className="h-full bg-gradient-to-r from-green-400 to-green-600"
                                initial={{ width: 0 }}
                                animate={isInView ? { width: '100%' } : {}}
                                transition={{ delay: 1, duration: 1.5 }}
                            />
                        </div>
                        <p className="text-xs text-gray-500">Scores computed per project. View results in your project.</p>
                    </div>
                </motion.div>

                {/* Knowledge Graph */}
                <motion.div
                    className="glass-card glow-border"
                    initial={{ opacity: 0, x: 50 }}
                    animate={isInView ? { opacity: 1, x: 0 } : {}}
                    transition={{ delay: 0.4, duration: 0.8 }}
                >
                    <h3 className="text-2xl font-bold text-gray-800 mb-6">Knowledge Graph Explorer</h3>

                    <div className="relative aspect-square bg-gradient-to-br from-blue-100 to-ice-100 rounded-xl overflow-hidden flex items-center justify-center">
                        {/* Central node */}
                        <motion.div
                            className="absolute w-16 h-16 rounded-full bg-gradient-to-br from-ice-400 to-blue-600 flex items-center justify-center text-white font-bold glow-border-strong z-10"
                            animate={{
                                scale: [1, 1.1, 1]
                            }}
                            transition={{
                                duration: 2,
                                repeat: Infinity
                            }}
                        >
                            AI
                        </motion.div>

                        {/* Connected nodes */}
                        {[...Array(6)].map((_, i) => {
                            const angle = (i * 60) * (Math.PI / 180);
                            const radius = 120;
                            const x = Math.cos(angle) * radius;
                            const y = Math.sin(angle) * radius;

                            return (
                                <g key={i}>
                                    {/* Connection line */}
                                    <motion.div
                                        className="absolute top-1/2 left-1/2 h-0.5 bg-gradient-to-r from-ice-400/50 to-transparent origin-left"
                                        style={{
                                            width: `${radius}px`,
                                            transform: `translate(-50%, -50%) rotate(${i * 60}deg)`
                                        }}
                                        initial={{ scaleX: 0 }}
                                        animate={isInView ? { scaleX: 1 } : {}}
                                        transition={{ delay: 0.5 + i * 0.1, duration: 0.5 }}
                                    />

                                    {/* Node */}
                                    <motion.div
                                        className="absolute w-12 h-12 rounded-full bg-white border-2 border-ice-400 flex items-center justify-center text-2xl glow-border"
                                        style={{
                                            left: `calc(50% + ${x}px)`,
                                            top: `calc(50% + ${y}px)`,
                                            transform: 'translate(-50%, -50%)'
                                        }}
                                        initial={{ scale: 0, opacity: 0 }}
                                        animate={isInView ? { scale: 1, opacity: 1 } : {}}
                                        transition={{ delay: 0.7 + i * 0.1, duration: 0.5 }}
                                        whileHover={{ scale: 1.2 }}
                                    >
                                        {['🔬', '📚', '💡', '🎯', '⚡', '🌟'][i]}
                                    </motion.div>
                                </g>
                            );
                        })}
                    </div>

                    <div className="mt-6 grid grid-cols-2 gap-4">
                        <div className="text-center">
                            <div className="text-2xl font-bold text-gray-700">Semantic Scholar</div>
                            <div className="text-sm text-gray-600">Research Papers</div>
                        </div>
                        <div className="text-center">
                            <div className="text-2xl font-bold text-gray-700">USPTO</div>
                            <div className="text-sm text-gray-600">Patent Database</div>
                        </div>
                    </div>
                    <p className="text-xs text-gray-500 mt-4 text-center">Evidence retrieved dynamically per project search.</p>
                </motion.div>
            </div>

            {/* Research Heatmap */}
            <motion.div
                className="mt-12 glass-card glow-border"
                initial={{ opacity: 0, y: 50 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ delay: 0.6, duration: 0.8 }}
            >
                <h3 className="text-2xl font-bold text-gray-800 mb-6">Dynamic Research Heatmap</h3>

                <div className="grid grid-cols-12 gap-2">
                    {[...Array(60)].map((_, i) => (
                        <motion.div
                            key={i}
                            className="aspect-square rounded-lg"
                            style={{
                                background: `linear-gradient(135deg, 
                  rgba(96, 165, 250, ${Math.random() * 0.8}), 
                  rgba(14, 165, 233, ${Math.random() * 0.6}))`
                            }}
                            initial={{ opacity: 0, scale: 0 }}
                            animate={isInView ? {
                                opacity: 1,
                                scale: 1,
                                backgroundColor: [
                                    `rgba(96, 165, 250, ${Math.random() * 0.8})`,
                                    `rgba(14, 165, 233, ${Math.random() * 0.6})`,
                                    `rgba(96, 165, 250, ${Math.random() * 0.8})`
                                ]
                            } : {}}
                            transition={{
                                delay: i * 0.01,
                                duration: 0.3,
                                backgroundColor: {
                                    duration: 3,
                                    repeat: Infinity,
                                    repeatType: "reverse"
                                }
                            }}
                            whileHover={{ scale: 1.2, zIndex: 10 }}
                        />
                    ))}
                </div>

                <div className="mt-6 flex items-center justify-between text-sm">
                    <span className="text-gray-600">Research Activity</span>
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 rounded bg-ice-200" />
                            <span className="text-gray-600">Low</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 rounded bg-ice-400" />
                            <span className="text-gray-600">Medium</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-4 h-4 rounded bg-blue-600" />
                            <span className="text-gray-600">High</span>
                        </div>
                    </div>
                </div>
            </motion.div>
        </section>
    );
};

export default IntelligenceEngine;
