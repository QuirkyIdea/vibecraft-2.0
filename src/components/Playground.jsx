import { motion } from 'framer-motion';

const Playground = () => {
    return (
        <section id="playground" className="min-h-screen py-24 px-6 bg-gray-50/50">
            <div className="max-w-7xl mx-auto">
                <div className="flex justify-between items-end mb-8">
                    <motion.h2
                        initial={{ opacity: 0 }}
                        whileInView={{ opacity: 1 }}
                        className="text-3xl font-bold text-gray-900"
                    >
                        Simulation Lab
                    </motion.h2>
                    <button className="btn-secondary text-sm py-2 px-6">Reset Environment</button>
                </div>

                <div className="glass-card h-[70vh] flex flex-col">
                    {/* Console Header */}
                    <div className="border-b border-gray-200 p-4 flex gap-4">
                        <div className="flex gap-2">
                            <div className="w-3 h-3 rounded-full bg-red-400"></div>
                            <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                            <div className="w-3 h-3 rounded-full bg-green-400"></div>
                        </div>
                        <span className="text-xs text-gray-400 font-mono ml-4">agent_simulator --mode=interactive</span>
                    </div>

                    {/* Console Body */}
                    <div className="flex-1 bg-gray-900/5 p-6 font-mono text-sm text-gray-600 overflow-y-auto">
                        <p className="mb-2">&gt; System initialized.</p>
                        <p className="mb-2">&gt; Loading specialized agents [Research, Patent, Novelty]... OK.</p>
                        <p className="mb-2">&gt; Waiting for input...</p>
                        <span className="w-2 h-4 bg-gray-400 inline-block animate-pulse"></span>
                    </div>

                    {/* Input Area */}
                    <div className="p-4 border-t border-gray-200 bg-white/50 backdrop-blur-md rounded-b-2xl">
                        <div className="flex gap-4">
                            <input
                                type="text"
                                placeholder="Enter specific instruction or hypothesis to test..."
                                className="flex-1 bg-transparent border-none outline-none text-gray-700 placeholder-gray-400"
                            />
                            <button className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white hover:bg-blue-700 transition-colors">
                                -&gt;
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default Playground;
