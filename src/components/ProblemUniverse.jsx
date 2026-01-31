import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef } from 'react';

const ProblemUniverse = () => {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: "-100px" });

    const problems = [
        {
            icon: '🧩',
            title: 'Research Complexity',
            description: 'Navigating vast literature databases and identifying research gaps is overwhelming and time-consuming.',
            color: 'from-blue-400 to-ice-500'
        },
        {
            icon: '📝',
            title: 'Patent Drafting Difficulties',
            description: 'Writing patent claims that are both novel and legally sound requires specialized expertise.',
            color: 'from-ice-400 to-cyan-500'
        },
        {
            icon: '⚠️',
            title: 'Novelty Risk',
            description: 'High risk of unknowingly duplicating existing research or infringing on existing patents.',
            color: 'from-cyan-400 to-blue-500'
        },
        {
            icon: '❓',
            title: 'Publication Uncertainty',
            description: 'Unclear which conferences or journals are the best fit for your research work.',
            color: 'from-blue-500 to-ice-600'
        },
        {
            icon: '⏰',
            title: 'Time-Consuming Workflows',
            description: 'Manual processes for literature review, drafting, and submission take months of valuable time.',
            color: 'from-ice-500 to-blue-600'
        }
    ];

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.15
            }
        }
    };

    const cardVariants = {
        hidden: { opacity: 0, y: 50, scale: 0.9 },
        visible: {
            opacity: 1,
            y: 0,
            scale: 1,
            transition: {
                duration: 0.6,
                ease: "easeOut"
            }
        }
    };

    return (
        <section ref={ref} className="section-container" id="problem-universe">
            <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.8 }}
                className="text-center mb-16"
            >
                <h2 className="text-5xl md:text-6xl font-bold text-gradient mb-6">
                    The Innovation Challenge
                </h2>
                <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                    Researchers and inventors face unprecedented complexity in bringing ideas to life
                </p>
            </motion.div>

            <motion.div
                variants={containerVariants}
                initial="hidden"
                animate={isInView ? "visible" : "hidden"}
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
            >
                {problems.map((problem, index) => (
                    <motion.div
                        key={problem.title}
                        variants={cardVariants}
                        whileHover={{
                            scale: 1.05,
                            y: -10,
                            transition: { duration: 0.3 }
                        }}
                        className="glass-card glow-border relative overflow-hidden group cursor-pointer"
                    >
                        {/* Animated gradient background */}
                        <motion.div
                            className={`absolute inset-0 bg-gradient-to-br ${problem.color} opacity-0 group-hover:opacity-10 transition-opacity duration-500`}
                        />

                        {/* Floating icon */}
                        <motion.div
                            className="text-6xl mb-6"
                            animate={{
                                y: [0, -10, 0],
                            }}
                            transition={{
                                duration: 3,
                                repeat: Infinity,
                                delay: index * 0.2
                            }}
                        >
                            {problem.icon}
                        </motion.div>

                        <h3 className="text-2xl font-bold text-gray-800 mb-4">
                            {problem.title}
                        </h3>

                        <p className="text-gray-600 leading-relaxed">
                            {problem.description}
                        </p>

                        {/* Animated corner accent */}
                        <motion.div
                            className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-ice-300/30 to-transparent rounded-bl-full"
                            initial={{ scale: 0, opacity: 0 }}
                            whileHover={{ scale: 1, opacity: 1 }}
                            transition={{ duration: 0.3 }}
                        />
                    </motion.div>
                ))}
            </motion.div>

            {/* Animated Timeline Connector */}
            <motion.div
                className="mt-20 relative"
                initial={{ opacity: 0 }}
                animate={isInView ? { opacity: 1 } : {}}
                transition={{ delay: 1, duration: 1 }}
            >
                <div className="h-1 bg-gradient-to-r from-transparent via-ice-400 to-transparent rounded-full" />
                <motion.div
                    className="absolute top-1/2 left-0 w-4 h-4 bg-ice-500 rounded-full -translate-y-1/2 glow-border-strong"
                    animate={{
                        x: ['0%', '100%'],
                        scale: [1, 1.5, 1]
                    }}
                    transition={{
                        duration: 4,
                        repeat: Infinity,
                        ease: "easeInOut"
                    }}
                />
            </motion.div>

            <motion.div
                className="text-center mt-16"
                initial={{ opacity: 0, y: 30 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ delay: 1.2, duration: 0.8 }}
            >
                <p className="text-2xl font-semibold text-gradient">
                    Inventix AI solves all of these challenges with intelligent automation
                </p>
            </motion.div>
        </section>
    );
};

export default ProblemUniverse;
