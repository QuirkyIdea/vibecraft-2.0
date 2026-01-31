import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef, useState } from 'react';

const PlatformOverview = () => {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: "-100px" });
    const [activeStep, setActiveStep] = useState(0);

    const pipeline = [
        { icon: '💡', label: 'Idea Input', description: 'Submit your research concept' },
        { icon: '🧠', label: 'Semantic Intelligence', description: 'AI analyzes and structures your idea' },
        { icon: '🔍', label: 'Novelty Analysis', description: 'Deep search across global databases' },
        { icon: '⚖️', label: 'Claim Risk Engine', description: 'Assess patent infringement risks' },
        { icon: '👨‍🏫', label: 'AI Research Mentor', description: 'Get expert guidance and feedback' },
        { icon: '✍️', label: 'Draft Generator', description: 'Auto-generate papers and patents' },
        { icon: '🚀', label: 'Submission Engine', description: 'Smart submission recommendations' },
        { icon: '📄', label: 'Publication & Filing', description: 'Track and manage submissions' }
    ];

    return (
        <section ref={ref} className="section-container bg-gradient-to-b from-transparent to-ice-50/50" id="platform">
            <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.8 }}
                className="text-center mb-20"
            >
                <h2 className="text-5xl md:text-6xl font-bold text-gradient mb-6">
                    Inventix AI Platform
                </h2>
                <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                    End-to-end intelligent pipeline from idea to publication
                </p>
            </motion.div>

            {/* Interactive Pipeline */}
            <div className="relative max-w-6xl mx-auto">
                {/* Connection Lines */}
                <div className="absolute top-1/2 left-0 right-0 h-1 bg-gradient-to-r from-ice-300 via-blue-400 to-ice-300 -translate-y-1/2 hidden lg:block" />

                {/* Animated Data Flow */}
                <motion.div
                    className="absolute top-1/2 left-0 w-8 h-8 -translate-y-1/2 hidden lg:block"
                    animate={{
                        x: ['0%', '1200%'],
                        opacity: [0, 1, 1, 0]
                    }}
                    transition={{
                        duration: 8,
                        repeat: Infinity,
                        ease: "linear"
                    }}
                >
                    <div className="w-full h-full rounded-full bg-gradient-to-r from-ice-400 to-blue-500 glow-border-strong" />
                </motion.div>

                {/* Pipeline Steps */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 relative z-10">
                    {pipeline.map((step, index) => (
                        <motion.div
                            key={step.label}
                            initial={{ opacity: 0, y: 50 }}
                            animate={isInView ? { opacity: 1, y: 0 } : {}}
                            transition={{ delay: index * 0.1, duration: 0.6 }}
                            onMouseEnter={() => setActiveStep(index)}
                            whileHover={{ scale: 1.05, y: -10 }}
                            className={`glass-card text-center cursor-pointer transition-all duration-300 ${activeStep === index ? 'glow-border-strong' : 'glow-border'
                                }`}
                        >
                            {/* Step Number */}
                            <div className="absolute -top-4 -left-4 w-8 h-8 rounded-full bg-gradient-to-br from-ice-400 to-blue-600 flex items-center justify-center text-white font-bold text-sm glow-border-strong">
                                {index + 1}
                            </div>

                            {/* Icon */}
                            <motion.div
                                className="text-5xl mb-4"
                                animate={{
                                    scale: activeStep === index ? [1, 1.2, 1] : 1,
                                    rotate: activeStep === index ? [0, 5, -5, 0] : 0
                                }}
                                transition={{ duration: 0.5 }}
                            >
                                {step.icon}
                            </motion.div>

                            {/* Label */}
                            <h3 className="text-lg font-bold text-gray-800 mb-2">
                                {step.label}
                            </h3>

                            {/* Description */}
                            <p className="text-sm text-gray-600">
                                {step.description}
                            </p>

                            {/* Animated Progress Bar */}
                            <motion.div
                                className="mt-4 h-1 bg-gradient-to-r from-ice-400 to-blue-500 rounded-full"
                                initial={{ width: 0 }}
                                animate={{ width: activeStep === index ? '100%' : '0%' }}
                                transition={{ duration: 0.5 }}
                            />
                        </motion.div>
                    ))}
                </div>
            </div>

            {/* Data Stream Visualization */}
            <motion.div
                className="mt-20 glass-card glow-border max-w-4xl mx-auto p-12"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={isInView ? { opacity: 1, scale: 1 } : {}}
                transition={{ delay: 1, duration: 0.8 }}
            >
                <h3 className="text-3xl font-bold text-center text-gradient mb-8">
                    Real-Time Intelligence Flow
                </h3>

                <div className="relative h-40 bg-gradient-to-r from-ice-100 via-blue-100 to-ice-100 rounded-xl overflow-hidden">
                    {/* Animated data packets */}
                    {[...Array(5)].map((_, i) => (
                        <motion.div
                            key={i}
                            className="absolute top-1/2 w-12 h-12 rounded-lg bg-gradient-to-br from-ice-400 to-blue-500 -translate-y-1/2 flex items-center justify-center text-white font-bold glow-border-strong"
                            animate={{
                                x: ['-10%', '110%'],
                                y: [0, -20, 0, 20, 0]
                            }}
                            transition={{
                                duration: 5,
                                repeat: Infinity,
                                delay: i * 1,
                                ease: "linear"
                            }}
                        >
                            📊
                        </motion.div>
                    ))}

                    {/* Background grid */}
                    <div className="absolute inset-0 opacity-20">
                        <div className="grid grid-cols-12 h-full">
                            {[...Array(12)].map((_, i) => (
                                <div key={i} className="border-r border-ice-300" />
                            ))}
                        </div>
                    </div>
                </div>

                <p className="text-center text-gray-600 mt-6">
                    Watch your ideas transform into validated research in real-time
                </p>
            </motion.div>
        </section>
    );
};

export default PlatformOverview;
