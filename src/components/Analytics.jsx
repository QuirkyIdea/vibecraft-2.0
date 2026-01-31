import { motion } from 'framer-motion';

const Analytics = () => {
    return (
        <section id="analytics" className="min-h-screen py-24 px-6 relative overflow-hidden">
            <div className="max-w-7xl mx-auto">
                <motion.h2
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    className="text-3xl font-bold mb-8 text-gray-900"
                >
                    Decision Intelligence
                </motion.h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 h-[500px]">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        className="glass-card flex items-center justify-center text-gray-400"
                    >
                        [Research Trend Graph Placeholder - Recharts would go here]
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.2 }}
                        className="glass-card flex items-center justify-center text-gray-400"
                    >
                        [Patent Citation Network Placeholder - D3.js would go here]
                    </motion.div>
                </div>
            </div>
        </section>
    );
};

export default Analytics;
