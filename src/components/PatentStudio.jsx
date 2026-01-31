import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef, useState } from 'react';

const PatentStudio = () => {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: "-100px" });
    const [riskLevel, setRiskLevel] = useState(15);

    const features = [
        {
            icon: '🔍',
            title: 'Prior Art Search Engine',
            description: 'Deep search across 100M+ global patents and publications',
            capability: 'Global coverage'
        },
        {
            icon: '⚖️',
            title: 'Claim Similarity Analyzer',
            description: 'AI-powered semantic analysis of patent claims',
            capability: '99.2% precision'
        },
        {
            icon: '📊',
            title: 'Patent Risk Predictor',
            description: 'Predict infringement risks before filing',
            capability: 'Risk assessment'
        },
        {
            icon: '🤖',
            title: 'Automated Drafting Assistant',
            description: 'Generate patent-ready claims and descriptions',
            capability: 'Auto-generation'
        },
        {
            icon: '📋',
            title: 'Compliance & Filing Generator',
            description: 'Format for USPTO, EPO, and other patent offices',
            capability: 'Multi-jurisdiction'
        }
    ];

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
                    AI-powered patent analysis and drafting for bulletproof IP protection
                </p>
            </motion.div>

            {/* Features Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
                {features.map((feature, index) => (
                    <motion.div
                        key={feature.title}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={isInView ? { opacity: 1, scale: 1 } : {}}
                        transition={{ delay: index * 0.1, duration: 0.6 }}
                        whileHover={{ scale: 1.05, y: -10 }}
                        className="glass-card glow-border group cursor-pointer"
                    >
                        <motion.div
                            className="text-5xl mb-4"
                            animate={{
                                rotate: [0, 10, -10, 0]
                            }}
                            transition={{
                                duration: 3,
                                repeat: Infinity,
                                delay: index * 0.4
                            }}
                        >
                            {feature.icon}
                        </motion.div>

                        <h3 className="text-xl font-bold text-gray-800 mb-3">
                            {feature.title}
                        </h3>

                        <p className="text-gray-600 mb-4 leading-relaxed">
                            {feature.description}
                        </p>

                        <div className="inline-block px-3 py-1 rounded-full bg-gradient-to-r from-ice-100 to-blue-100 text-ice-700 text-sm font-semibold">
                            {feature.capability}
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* Risk Predictor Demo */}
            <motion.div
                className="glass-card glow-border-strong max-w-4xl mx-auto"
                initial={{ opacity: 0, y: 50 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ delay: 0.6, duration: 0.8 }}
            >
                <h3 className="text-3xl font-bold text-center text-gradient mb-8">
                    Live Patent Risk Assessment
                </h3>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Risk Gauge */}
                    <div className="relative">
                        <div className="text-center mb-6">
                            <div className="text-sm text-gray-600 mb-2">Infringement Risk Level</div>
                            <motion.div
                                className="text-6xl font-bold"
                                animate={{
                                    color: riskLevel < 30 ? '#10b981' : riskLevel < 70 ? '#f59e0b' : '#ef4444'
                                }}
                            >
                                {riskLevel}%
                            </motion.div>
                        </div>

                        {/* Circular gauge */}
                        <div className="relative w-64 h-64 mx-auto">
                            <svg className="w-full h-full transform -rotate-90">
                                {/* Background circle */}
                                <circle
                                    cx="128"
                                    cy="128"
                                    r="100"
                                    fill="none"
                                    stroke="#e0f2fe"
                                    strokeWidth="20"
                                />
                                {/* Progress circle */}
                                <motion.circle
                                    cx="128"
                                    cy="128"
                                    r="100"
                                    fill="none"
                                    stroke="url(#riskGradient)"
                                    strokeWidth="20"
                                    strokeLinecap="round"
                                    strokeDasharray={`${2 * Math.PI * 100}`}
                                    initial={{ strokeDashoffset: 2 * Math.PI * 100 }}
                                    animate={isInView ? {
                                        strokeDashoffset: 2 * Math.PI * 100 * (1 - riskLevel / 100)
                                    } : {}}
                                    transition={{ duration: 2, delay: 0.5 }}
                                />
                                <defs>
                                    <linearGradient id="riskGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                        <stop offset="0%" stopColor="#60a5fa" />
                                        <stop offset="100%" stopColor="#3b82f6" />
                                    </linearGradient>
                                </defs>
                            </svg>

                            {/* Center icon */}
                            <div className="absolute inset-0 flex items-center justify-center">
                                <motion.div
                                    className="text-5xl"
                                    animate={{
                                        scale: [1, 1.2, 1]
                                    }}
                                    transition={{
                                        duration: 2,
                                        repeat: Infinity
                                    }}
                                >
                                    {riskLevel < 30 ? '✅' : riskLevel < 70 ? '⚠️' : '🚨'}
                                </motion.div>
                            </div>
                        </div>

                        {/* Risk slider */}
                        <div className="mt-8">
                            <input
                                type="range"
                                min="0"
                                max="100"
                                value={riskLevel}
                                onChange={(e) => setRiskLevel(parseInt(e.target.value))}
                                className="w-full h-2 bg-ice-200 rounded-lg appearance-none cursor-pointer"
                                style={{
                                    background: `linear-gradient(to right, #60a5fa ${riskLevel}%, #e0f2fe ${riskLevel}%)`
                                }}
                            />
                            <div className="flex justify-between text-xs text-gray-600 mt-2">
                                <span>Low Risk</span>
                                <span>High Risk</span>
                            </div>
                        </div>
                    </div>

                    {/* Analysis Results */}
                    <div className="space-y-4">
                        <h4 className="text-xl font-bold text-gray-800 mb-4">Analysis Results</h4>

                        {[
                            { label: 'Similar Patents Found', value: '847', status: 'warning' },
                            { label: 'Exact Claim Matches', value: '3', status: 'danger' },
                            { label: 'Semantic Similarity', value: '76%', status: 'warning' },
                            { label: 'Novelty Score', value: '24%', status: 'danger' },
                            { label: 'Recommended Actions', value: '5', status: 'info' }
                        ].map((item, i) => (
                            <motion.div
                                key={item.label}
                                className="p-4 rounded-xl bg-gradient-to-r from-ice-50 to-blue-50 border-l-4"
                                style={{
                                    borderColor: item.status === 'danger' ? '#ef4444' :
                                        item.status === 'warning' ? '#f59e0b' : '#60a5fa'
                                }}
                                initial={{ opacity: 0, x: 20 }}
                                animate={isInView ? { opacity: 1, x: 0 } : {}}
                                transition={{ delay: 1 + i * 0.1, duration: 0.5 }}
                            >
                                <div className="flex items-center justify-between">
                                    <span className="font-medium text-gray-700">{item.label}</span>
                                    <span className="text-xl font-bold text-gradient">{item.value}</span>
                                </div>
                            </motion.div>
                        ))}

                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="w-full btn-primary mt-6"
                        >
                            Generate Full Report
                        </motion.button>
                    </div>
                </div>
            </motion.div>
        </section>
    );
};

export default PatentStudio;
