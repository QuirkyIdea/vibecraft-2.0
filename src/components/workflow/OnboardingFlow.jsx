import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useWorkflow } from '../../context/WorkflowContext';

const DOMAINS = [
    { id: 'AI', label: 'Artificial Intelligence', icon: '🧠', color: 'blue' },
    { id: 'BIOTECH', label: 'Biotechnology', icon: '🧬', color: 'green' },
    { id: 'MECHANICAL', label: 'Mechanical Eng.', icon: '⚙️', color: 'orange' },
    { id: 'MATERIALS', label: 'Material Science', icon: '🧪', color: 'purple' },
    { id: 'SOFTWARE', label: 'Software Eng.', icon: '💻', color: 'indigo' },
    { id: 'ELECTRONICS', label: 'Electronics', icon: '⚡', color: 'yellow' },
    { id: 'MEDICAL', label: 'Medical Research', icon: '🩺', color: 'red' }
];

const OnboardingFlow = () => {
    const {
        creationStage,
        startNewProject, // We reuse this to update data
        startAnalysis, // Renamed to confirmProjectCreation in context potentially? No, we need to map it.
        newProjectData,
        setNewProjectData,
        // We need to map the old "startUpload" to just updating local state or context
        setCreationStage,
        confirmProjectCreation
    } = useWorkflow();

    // Map the context functions to what the UI expects
    // Logic: 
    // Step 1 (Idea) calls onNext -> Updates data, sets stage to UPLOAD
    // Step 2 (Upload) calls onNext -> Sets stage to SEGREGATION (animations start)

    // We already have startNewProject which sets stage to UPLOAD. 
    // We need a helper to update data and move to UPLOAD.

    const handleTypeSelection = (type) => {
        setNewProjectData(prev => ({ ...prev, projectType: type }));
        setCreationStage('IDEA');
    }

    const handleIdeaSubmit = (data) => {
        setNewProjectData(prev => ({ ...prev, ...data }));
        setCreationStage('UPLOAD');
    };

    const handleUploadComplete = (files) => {
        // Trigger the animation pipeline
        setCreationStage('SEGREGATION');
        // The PipelineAnimation component (rendered by DashboardLayout) will handle the timeout -> Confirm
    };

    if (creationStage === 'SEGREGATION' || creationStage === 'PIPELINE') return null; // Handled by PipelineAnimation

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-white via-ice-50 to-blue-50/30 p-6 z-50 fixed inset-0">
            <div className="max-w-4xl w-full">
                <AnimatePresence mode="wait">
                    {creationStage === 'TYPE' && (
                        <TypeSelection key="type" onSelect={handleTypeSelection} />
                    )}
                    {creationStage === 'IDEA' && (
                        <IdeaInput
                            key="idea"
                            ideaData={newProjectData}
                            setIdeaData={setNewProjectData}
                            domain={newProjectData.domain}
                            setDomain={(d) => setNewProjectData(prev => ({ ...prev, domain: d }))}
                            onNext={() => handleIdeaSubmit(newProjectData)}
                        />
                    )}
                    {creationStage === 'UPLOAD' && (
                        <EvidenceUpload
                            key="upload"
                            onNext={handleUploadComplete}
                        />
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
};

const TypeSelection = ({ onSelect }) => (
    <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, x: -50 }}
        className="glass-card glow-border-strong p-10 text-center"
    >
        <h1 className="text-4xl font-bold mb-4">
            <span className="text-gray-900">What do you want to build?</span>
        </h1>
        <p className="text-gray-500 mb-12">Select the type of intelligence pipeline to initialize.</p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <button
                onClick={() => onSelect('RESEARCH')}
                className="group p-8 rounded-3xl border border-gray-200 hover:border-blue-400 hover:bg-blue-50/30 transition-all text-left relative overflow-hidden"
            >
                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity text-8xl">🧠</div>
                <div className="text-4xl mb-4">🔬</div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">Research Project</h3>
                <p className="text-gray-500 text-sm">Literature synthesis, gap analysis, and experimental planning.</p>
            </button>

            <button
                onClick={() => onSelect('PATENT')}
                className="group p-8 rounded-3xl border border-gray-200 hover:border-orange-400 hover:bg-orange-50/30 transition-all text-left relative overflow-hidden"
            >
                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity text-8xl">⚖️</div>
                <div className="text-4xl mb-4">📜</div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">Patent Project</h3>
                <p className="text-gray-500 text-sm">Novelty search, claim optimization, and infringement risk analysis.</p>
            </button>
        </div>
    </motion.div>
);

const IdeaInput = ({ ideaData, setIdeaData, domain, setDomain, onNext }) => {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, x: -50 }}
            className="glass-card glow-border-strong p-10"
        >
            <h1 className="text-4xl font-bold mb-2">
                <span className="text-gray-400">Step 1:</span> <span className="text-gradient">Initialize Research</span>
            </h1>
            <p className="text-gray-500 mb-8">Define your problem statement and select a domain to configure the AI.</p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                <div className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Research Title / Concept Name</label>
                        <input
                            type="text"
                            className="w-full bg-white/50 border border-gray-200 rounded-xl px-4 py-3 outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 transition-all"
                            placeholder="e.g., Autonomous Drone Navigation System"
                            value={ideaData.title}
                            onChange={e => setIdeaData({ ...ideaData, title: e.target.value })}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Problem Statement</label>
                        <textarea
                            className="w-full bg-white/50 border border-gray-200 rounded-xl px-4 py-3 outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 transition-all h-32 resize-none"
                            placeholder="Describe the core problem you are solving..."
                            value={ideaData.description}
                            onChange={e => setIdeaData({ ...ideaData, description: e.target.value })}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Expected Outcome</label>
                        <input
                            type="text"
                            className="w-full bg-white/50 border border-gray-200 rounded-xl px-4 py-3 outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 transition-all"
                            placeholder="e.g., Increase efficiency by 20%"
                            value={ideaData.outcome}
                            onChange={e => setIdeaData({ ...ideaData, outcome: e.target.value })}
                        />
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-4">Select Domain Scope</label>
                    <div className="grid grid-cols-2 gap-3">
                        {DOMAINS.map(d => (
                            <motion.button
                                key={d.id}
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={() => setDomain(d.id)}
                                className={`p-4 rounded-xl border text-left transition-all ${domain === d.id
                                    ? `bg-${d.color}-50 border-${d.color}-500 ring-2 ring-${d.color}-200`
                                    : 'bg-white/40 border-gray-200 hover:bg-white/80'
                                    }`}
                            >
                                <span className="text-2xl mb-2 block">{d.icon}</span>
                                <span className={`text-sm font-semibold ${domain === d.id ? `text-${d.color}-700` : 'text-gray-600'}`}>
                                    {d.label}
                                </span>
                            </motion.button>
                        ))}
                    </div>
                </div>
            </div>

            <div className="flex justify-end">
                <button
                    onClick={onNext}
                    disabled={!domain || !ideaData.title}
                    className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    Continue to Evidence Upload
                    <span>→</span>
                </button>
            </div>
        </motion.div>
    );
};

const EvidenceUpload = ({ onNext }) => {
    const [files, setFiles] = useState([]);
    const [isDragging, setIsDragging] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const fileInputRef = useRef(null);

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        const droppedFiles = Array.from(e.dataTransfer.files);
        if (droppedFiles.length > 0) processFiles(droppedFiles);
    };

    const handleFileSelect = (e) => {
        if (e.target.files) {
            const selectedFiles = Array.from(e.target.files);
            if (selectedFiles.length > 0) processFiles(selectedFiles);
        }
    };

    const processFiles = (newFiles) => {
        const fileEntries = newFiles.map(file => ({
            name: file.name,
            size: (file.size / 1024 / 1024).toFixed(2),
            progress: 0,
            status: 'uploading'
        }));

        setFiles(prev => [...prev, ...fileEntries]);

        // Simulate upload progress
        fileEntries.forEach((file, index) => {
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 10 + 5;
                if (progress >= 100) {
                    progress = 100;
                    clearInterval(interval);
                    updateFileStatus(file.name, 'completed');
                }
                updateFileProgress(file.name, progress);
            }, 200 + index * 100);
        });
    };

    const updateFileProgress = (fileName, progress) => {
        setFiles(prev => prev.map(f =>
            f.name === fileName ? { ...f, progress } : f
        ));
    };

    const updateFileStatus = (fileName, status) => {
        setFiles(prev => prev.map(f =>
            f.name === fileName ? { ...f, status } : f
        ));
    };

    const handleContinue = () => {
        setIsProcessing(true);
        setTimeout(() => {
            onNext(files);
        }, 1500);
    };

    return (
        <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="glass-card glow-border-strong p-10 max-w-4xl mx-auto"
        >
            <h1 className="text-4xl font-bold mb-2">
                <span className="text-gray-400">Step 2:</span> <span className="text-gradient">Evidence Upload</span>
            </h1>
            <p className="text-gray-500 mb-8">Upload technical documentation to seed the AI knowledge base.</p>

            {/* Drop Zone */}
            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all cursor-pointer mb-8 relative overflow-hidden
                    ${isDragging ? 'border-blue-500 bg-blue-50/50 scale-[1.02]' : 'border-blue-200 bg-blue-50/10 hover:bg-blue-50/30'}
                `}
            >
                <input
                    type="file"
                    multiple
                    className="hidden"
                    ref={fileInputRef}
                    onChange={handleFileSelect}
                />

                <div className="relative z-10">
                    <div className="text-6xl mb-4">📂</div>
                    <h3 className="text-xl font-semibold text-gray-800 mb-2">
                        {isDragging ? 'Drop Files Now' : 'Drag & Drop Files'}
                    </h3>
                    <p className="text-gray-500 text-sm mb-6">PDF, DOCX, TXT supported (Max 50MB)</p>
                    <button className="bg-white border border-gray-300 px-6 py-2 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
                        Browse Files
                    </button>
                </div>
            </div>

            {/* File List */}
            <div className="space-y-3 mb-8 max-h-60 overflow-y-auto custom-scrollbar">
                <AnimatePresence>
                    {files.map((file) => (
                        <motion.div
                            key={file.name}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-white border border-gray-100 p-4 rounded-xl flex items-center justify-between shadow-sm"
                        >
                            <div className="flex items-center gap-4 flex-1">
                                <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center text-xl">
                                    📄
                                </div>
                                <div className="flex-1">
                                    <div className="flex justify-between mb-1">
                                        <h4 className="text-sm font-medium text-gray-800 truncate max-w-[200px]">{file.name}</h4>
                                        <span className="text-xs text-gray-500">{file.size} MB</span>
                                    </div>
                                    <div className="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden">
                                        <motion.div
                                            className="h-full bg-blue-500"
                                            initial={{ width: 0 }}
                                            animate={{ width: `${file.progress}%` }}
                                        />
                                    </div>
                                </div>
                            </div>
                            <div className="ml-4">
                                {file.progress === 100 ? (
                                    <span className="text-green-500 text-xs font-bold bg-green-50 px-2 py-1 rounded-md">READY</span>
                                ) : (
                                    <span className="text-blue-500 text-xs font-bold">{Math.round(file.progress)}%</span>
                                )}
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>

            <div className="flex justify-between items-center border-t border-gray-100 pt-6">
                <button className="text-gray-400 text-sm hover:text-gray-600 transition-colors">Skip for now</button>
                <button
                    onClick={handleContinue}
                    disabled={files.length === 0 || isProcessing}
                    className={`btn-primary flex items-center gap-2 min-w-[160px] justify-center ${files.length === 0 ? 'opacity-50 cursor-not-allowed' : ''
                        }`}
                >
                    {isProcessing ? (
                        <>
                            <span className="animate-spin">⚙️</span> Processing...
                        </>
                    ) : (
                        <>
                            Initialize Pipeline <span>✨</span>
                        </>
                    )}
                </button>
            </div>
        </motion.div>
    );
};

export default OnboardingFlow;
