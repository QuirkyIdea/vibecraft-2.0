import { motion } from 'framer-motion';
import { useWorkflow } from '../context/WorkflowContext';

const CommandCenter = () => {
    const { domain } = useWorkflow();
    const domainLabel = domain ? `${domain} Research` : 'Research';

    return (
        <section id="command-center" className="min-h-screen pt-24 px-6 bg-gradient-to-br from-white via-blue-50 to-indigo-50/30">
            <div className="max-w-7xl mx-auto">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                    className="mb-10"
                >
                    <h1 className="text-4xl font-bold mb-2">
                        <span className="text-gray-900">{domainLabel}</span> <span className="text-gradient">Control Room</span>
                    </h1>
                    <p className="text-gray-500">System Status: <span className="text-green-500 font-semibold">● Online</span> | Active Agents: 12 | Domain: {domain || 'General'}</p>
                </motion.div>

                {/* KPI Grid */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
                    {[
                        { label: 'Active Projects', value: '4', change: '+2', color: 'blue' },
                        { label: 'Pending Reviews', value: '18', change: '-5', color: 'orange' },
                        { label: 'Novelty Score', value: '94%', change: '+1.2%', color: 'purple' },
                        { label: 'System Load', value: '23%', change: 'Stable', color: 'green' }
                    ].map((stat, index) => (
                        <motion.div
                            key={stat.label}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                            whileHover={{ scale: 1.02 }}
                            className="bg-white/60 backdrop-blur-xl border border-white/40 p-6 rounded-2xl shadow-lg"
                        >
                            <h3 className="text-gray-500 text-sm font-medium mb-2">{stat.label}</h3>
                            <div className="flex items-end gap-3">
                                <span className={`text-3xl font-bold text-${stat.color}-600`}>{stat.value}</span>
                                <span className="text-xs text-gray-400 mb-1">{stat.change}</span>
                            </div>
                        </motion.div>
                    ))}
                </div>

                {/* Main Dashboard Layout */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Activity Feed */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.4 }}
                        className="lg:col-span-2 glass-card h-[600px] overflow-hidden relative"
                    >
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-xl font-semibold text-gray-800">Live Intelligence Feed</h2>
                            <div className="flex gap-2">
                                <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
                                <span className="text-xs text-blue-500 font-medium">REAL-TIME</span>
                            </div>
                        </div>

                        <div className="space-y-4">
                            {[
                                { agent: 'Novelty Detector', action: 'Flagged potential conflict in claim #4', time: '2m ago', type: 'alert' },
                                { agent: 'Research Supervisor', action: 'Completed synthesis of 15 papers', time: '5m ago', type: 'success' },
                                { agent: 'Patent Drafter', action: 'Drafting Embodiment 3...', time: '12m ago', type: 'process' },
                                { agent: 'Knowledge Graph', action: 'Linked "Transformer" to "Attention"', time: '15m ago', type: 'info' }
                            ].map((item, i) => (
                                <div key={i} className="flex items-start gap-4 p-4 rounded-xl bg-white/40 border border-white/60 hover:bg-white/60 transition-colors">
                                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 
                                        ${item.type === 'alert' ? 'bg-red-100 text-red-600' :
                                            item.type === 'success' ? 'bg-green-100 text-green-600' :
                                                item.type === 'process' ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'}`}
                                    >
                                        <span className="text-xs font-bold">AI</span>
                                    </div>
                                    <div className="flex-1">
                                        <div className="flex justify-between">
                                            <h4 className="text-sm font-semibold text-gray-800">{item.agent}</h4>
                                            <span className="text-xs text-gray-400">{item.time}</span>
                                        </div>
                                        <p className="text-sm text-gray-600 mt-1">{item.action}</p>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Simulation of scanning lines or grid */}
                        <div className="absolute inset-0 pointer-events-none bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20"></div>
                    </motion.div>

                    {/* System Status / Quick Actions */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.5 }}
                        className="space-y-8"
                    >
                        {/* Agent Status */}
                        <div className="glass-card">
                            <h3 className="text-lg font-semibold mb-4 text-gray-800">Agent Status</h3>
                            <div className="space-y-3">
                                {['Research Supervisor', 'Patent Drafter', 'Compliance Officer'].map(agent => (
                                    <div key={agent} className="flex items-center justify-between">
                                        <span className="text-sm text-gray-600">{agent}</span>
                                        <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-700 border border-green-200">IDLE</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Quick Actions */}
                        <div className="glass-card">
                            <h3 className="text-lg font-semibold mb-4 text-gray-800">Quick Actions</h3>
                            <div className="grid grid-cols-2 gap-3">
                                {['New Research', 'Draft Patent', 'Scan Novelty', 'View Graph'].map(action => (
                                    <button key={action} className="p-3 rounded-xl bg-white/50 border border-white/60 hover:bg-blue-50/50 hover:border-blue-200 transition-all text-sm font-medium text-gray-700 text-left">
                                        {action}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </motion.div>
                </div>
            </div>
        </section>
    );
};

export default CommandCenter;
