import { motion } from 'framer-motion';
import NeuralBackground from './NeuralBackground';

const HomePage = () => {
    return (
        <div className="min-h-screen bg-white pt-24 pb-20 overflow-hidden relative">
            <NeuralBackground />
            {/* Hero Section */}
            <section className="relative px-6 max-w-7xl mx-auto text-center mb-32">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8 }}
                >
                    <h1 className="text-6xl md:text-8xl font-bold tracking-tight mb-8">
                        <span className="text-gray-900">INVENTIX</span> <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-cyan-400">AI</span>
                    </h1>
                    <p className="text-xl md:text-2xl text-gray-500 max-w-3xl mx-auto font-light leading-relaxed">
                        The world's first <span className="text-blue-600 font-medium">Research & Patent Intelligence Operating System</span>.
                        Transforming raw ideas into defensible innovation through autonomous multi-agent orchestration.
                    </p>
                </motion.div>

                {/* Simulated Pipeline Visualization */}
                <div className="mt-20 relative h-[300px] w-full max-w-5xl mx-auto rounded-3xl border border-gray-100 bg-gray-50/50 backdrop-blur-sm overflow-hidden flex items-center justify-center">
                    <div className="absolute inset-0 bg-grid-slate-100 [mask-image:linear-gradient(0deg,white,rgba(255,255,255,0.6))]"></div>
                    <div className="flex items-center gap-8 relative z-10">
                        {['User Idea', 'AI Brain', 'Multi-Agent Swarm', 'Knowledge Graph', 'Research Engine', 'Patent Engine', 'Output'].map((step, i) => (
                            <div key={i} className="flex items-center gap-4">
                                <motion.div
                                    className="bg-white border border-blue-100 shadow-sm px-4 py-2 rounded-lg text-xs font-semibold text-gray-600"
                                    animate={{
                                        boxShadow: ["0 0 0px rgba(0,0,0,0)", "0 0 20px rgba(59,130,246,0.2)", "0 0 0px rgba(0,0,0,0)"],
                                        borderColor: ["#DBEAFE", "#3B82F6", "#DBEAFE"]
                                    }}
                                    transition={{ duration: 2, repeat: Infinity, delay: i * 0.3 }}
                                >
                                    {step}
                                </motion.div>
                                {i < 6 && <div className="w-8 h-[2px] bg-blue-100"></div>}
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Feature Cards */}
            <section className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-3 gap-8">
                <FeatureCard
                    title="Multi-Agent Research Brain"
                    desc="Autonomous agents that read, synthesize, and critique millions of papers in real-time."
                    icon="🧠"
                />
                <FeatureCard
                    title="Patent Intelligence Engine"
                    desc="Real-time novelty scoring, prior-art radars, and automated claim drafting optimization."
                    icon="⚖️"
                />
                <FeatureCard
                    title="Innovation Workflow"
                    desc="End-to-end pipeline management from napkin sketch to publication-ready outcome."
                    icon="🚀"
                />
            </section>
        </div>
    );
};

const FeatureCard = ({ title, desc, icon }) => (
    <motion.div
        whileHover={{ y: -10 }}
        className="p-8 rounded-3xl bg-white border border-gray-100 shadow-xl shadow-blue-900/5 hover:border-blue-200 transition-all"
    >
        <div className="text-4xl mb-6 bg-blue-50 w-16 h-16 rounded-2xl flex items-center justify-center">{icon}</div>
        <h3 className="text-2xl font-bold text-gray-900 mb-4">{title}</h3>
        <p className="text-gray-500 leading-relaxed">{desc}</p>
    </motion.div>
);

export default HomePage;
