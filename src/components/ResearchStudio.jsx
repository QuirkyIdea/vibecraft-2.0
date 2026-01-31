import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef } from 'react';

const ResearchStudio = () => {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: "-100px" });

    const features = [
        {
            icon: '📖',
            title: 'AI Literature Review Engine',
            description: 'Automatically scan and summarize millions of research papers',
            stats: '2.4M+ papers',
            color: 'from-blue-400 to-ice-500'
        },
        {
            icon: '🔎',
            title: 'Gap Detection System',
            description: 'Identify unexplored research opportunities in your field',
            stats: '95% accuracy',
            color: 'from-ice-400 to-cyan-500'
        },
        {
            icon: '🗺️',
            title: 'Research Roadmap Generator',
            description: 'Create step-by-step research plans with AI guidance',
            stats: 'Smart planning',
            color: 'from-cyan-400 to-blue-500'
        },
        {
            icon: '🧪',
            title: 'Experiment Planning AI',
            description: 'Design optimal experiments with predictive modeling',
            stats: 'Optimized design',
            color: 'from-blue-500 to-ice-600'
        },
        {
            icon: '✍️',
            title: 'Paper Drafting Workspace',
            description: 'Collaborative AI-assisted writing environment',
            stats: 'Real-time assist',
            color: 'from-ice-500 to-blue-600'
        },
        {
            icon: '🎓',
            title: 'Conference Recommendation',
            description: 'Find the perfect venue for your research publication',
            stats: '5000+ venues',
            color: 'from-blue-600 to-ice-700'
        }
    ];

    return (
        <section ref={ref} className="section-container bg-gradient-to-b from-ice-50/50 to-transparent" id="research-studio">
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
                    Your AI-powered research laboratory for breakthrough discoveries
                </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {features.map((feature, index) => (
                    <motion.div
                        key={feature.title}
                        initial={{ opacity: 0, y: 50, rotateY: -15 }}
                        animate={isInView ? { opacity: 1, y: 0, rotateY: 0 } : {}}
                        transition={{ delay: index * 0.1, duration: 0.6 }}
                        whileHover={{
                            scale: 1.05,
                            y: -10,
                            rotateY: 5,
                            transition: { duration: 0.3 }
                        }}
                        className="glass-card glow-border relative overflow-hidden group perspective-1000"
                    >
                        {/* Gradient overlay */}
                        <motion.div
                            className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-10 transition-opacity duration-500`}
                        />

                        {/* Icon with animation */}
                        <motion.div
                            className="text-6xl mb-6 relative z-10"
                            animate={{
                                y: [0, -10, 0],
                                rotate: [0, 5, -5, 0]
                            }}
                            transition={{
                                duration: 4,
                                repeat: Infinity,
                                delay: index * 0.3
                            }}
                        >
                            {feature.icon}
                        </motion.div>

                        {/* Title */}
                        <h3 className="text-2xl font-bold text-gray-800 mb-4 relative z-10">
                            {feature.title}
                        </h3>

                        {/* Description */}
                        <p className="text-gray-600 leading-relaxed mb-6 relative z-10">
                            {feature.description}
                        </p>

                        {/* Stats badge */}
                        <motion.div
                            className="inline-block px-4 py-2 rounded-full bg-gradient-to-r from-ice-100 to-blue-100 text-ice-700 font-semibold text-sm relative z-10"
                            whileHover={{ scale: 1.1 }}
                        >
                            {feature.stats}
                        </motion.div>

                        {/* Animated corner glow */}
                        <motion.div
                            className="absolute -bottom-10 -right-10 w-32 h-32 rounded-full bg-gradient-to-br from-ice-400/30 to-blue-500/30 blur-2xl"
                            animate={{
                                scale: [1, 1.2, 1],
                                opacity: [0.3, 0.6, 0.3]
                            }}
                            transition={{
                                duration: 3,
                                repeat: Infinity,
                                delay: index * 0.2
                            }}
                        />
                    </motion.div>
                ))}
            </div>

            {/* Interactive Demo Section */}
            <motion.div
                className="mt-20 glass-card glow-border-strong max-w-5xl mx-auto"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={isInView ? { opacity: 1, scale: 1 } : {}}
                transition={{ delay: 0.8, duration: 0.8 }}
            >
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Left: Code/Input */}
                    <div>
                        <h3 className="text-2xl font-bold text-gray-800 mb-6">AI Research Assistant</h3>
                        <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-6 font-mono text-sm">
                            <div className="flex items-center gap-2 mb-4">
                                <div className="w-3 h-3 rounded-full bg-red-500" />
                                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                                <div className="w-3 h-3 rounded-full bg-green-500" />
                            </div>
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={isInView ? { opacity: 1 } : {}}
                                transition={{ delay: 1, duration: 0.5 }}
                            >
                                <div className="text-green-400">$ analyze-research</div>
                                <div className="text-blue-300 mt-2">&gt; Topic: "Quantum Machine Learning"</div>
                                <div className="text-gray-400 mt-2">&gt; Analyzing 2,847 papers...</div>
                                <motion.div
                                    className="text-yellow-300 mt-2"
                                    initial={{ width: 0 }}
                                    animate={isInView ? { width: '100%' } : {}}
                                    transition={{ delay: 1.5, duration: 2 }}
                                >
                                    &gt; [████████████████] 100%
                                </motion.div>
                                <div className="text-green-400 mt-2">✓ Analysis complete!</div>
                            </motion.div>
                        </div>
                    </div>

                    {/* Right: Output */}
                    <div>
                        <h3 className="text-2xl font-bold text-gray-800 mb-6">Insights Generated</h3>
                        <div className="space-y-4">
                            {[
                                { label: 'Research Gaps Found', value: '23', icon: '🎯' },
                                { label: 'Key Papers Identified', value: '156', icon: '📚' },
                                { label: 'Collaboration Opportunities', value: '12', icon: '🤝' },
                                { label: 'Funding Sources', value: '8', icon: '💰' }
                            ].map((item, i) => (
                                <motion.div
                                    key={item.label}
                                    className="flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-ice-100 to-blue-100"
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={isInView ? { opacity: 1, x: 0 } : {}}
                                    transition={{ delay: 1.5 + i * 0.1, duration: 0.5 }}
                                >
                                    <div className="flex items-center gap-3">
                                        <span className="text-2xl">{item.icon}</span>
                                        <span className="font-medium text-gray-700">{item.label}</span>
                                    </div>
                                    <span className="text-2xl font-bold text-gradient">{item.value}</span>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                </div>
            </motion.div>
        </section>
    );
};

export default ResearchStudio;
