/**
 * Inventix AI - Onboarding Flow
 * 
 * REFACTORED: Real API integration for project creation and file upload.
 * No more simulated delays or fake progress bars.
 */
import { useState, useRef } from 'react';
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
        newProjectData,
        setNewProjectData,
        setCreationStage,
        confirmProjectCreation,
        uploadFile
    } = useWorkflow();

    const [error, setError] = useState(null);

    const handleTypeSelection = (type) => {
        setNewProjectData(prev => ({ ...prev, projectType: type }));
        setCreationStage('IDEA');
    };

    const handleIdeaSubmit = () => {
        if (!newProjectData.title || !newProjectData.domain) {
            setError('Please fill in all required fields');
            return;
        }
        setError(null);
        setCreationStage('UPLOAD');
    };

    if (creationStage === 'PROCESSING') {
        return <ProcessingView />;
    }

    if (creationStage === 'IDLE' || !['TYPE', 'IDEA', 'UPLOAD'].includes(creationStage)) {
        return null;
    }

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
                            onNext={handleIdeaSubmit}
                            error={error}
                        />
                    )}
                    {creationStage === 'UPLOAD' && (
                        <EvidenceUpload
                            key="upload"
                            projectData={newProjectData}
                            uploadFile={uploadFile}
                            confirmProjectCreation={confirmProjectCreation}
                            setCreationStage={setCreationStage}
                        />
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
};

const ProcessingView = () => (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-white via-ice-50 to-blue-50/30 p-6 z-50 fixed inset-0">
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card glow-border-strong p-10 text-center max-w-md"
        >
            <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                className="text-6xl mb-6"
            >
                ⚙️
            </motion.div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Creating Project...</h2>
            <p className="text-gray-500">Connecting to backend and initializing your workspace.</p>
        </motion.div>
    </div>
);

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

const IdeaInput = ({ ideaData, setIdeaData, domain, setDomain, onNext, error }) => {
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

            {error && (
                <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
                    ⚠️ {error}
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                <div className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Research Title / Concept Name *</label>
                        <input
                            type="text"
                            className="w-full bg-white/50 border border-gray-200 rounded-xl px-4 py-3 outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 transition-all"
                            placeholder="e.g., Autonomous Drone Navigation System"
                            value={ideaData.title}
                            onChange={e => setIdeaData({ ...ideaData, title: e.target.value })}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Problem Statement / Idea Description</label>
                        <textarea
                            className="w-full bg-white/50 border border-gray-200 rounded-xl px-4 py-3 outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 transition-all h-32 resize-none"
                            placeholder="Describe the core problem you are solving..."
                            value={ideaData.description}
                            onChange={e => setIdeaData({ ...ideaData, description: e.target.value })}
                        />
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-4">Select Domain Scope *</label>
                    <div className="grid grid-cols-2 gap-3">
                        {DOMAINS.map(d => (
                            <motion.button
                                key={d.id}
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={() => setDomain(d.id)}
                                className={`p-4 rounded-xl border text-left transition-all ${domain === d.id
                                    ? `bg-blue-50 border-blue-500 ring-2 ring-blue-200`
                                    : 'bg-white/40 border-gray-200 hover:bg-white/80'
                                    }`}
                            >
                                <span className="text-2xl mb-2 block">{d.icon}</span>
                                <span className={`text-sm font-semibold ${domain === d.id ? 'text-blue-700' : 'text-gray-600'}`}>
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

const EvidenceUpload = ({ projectData, uploadFile, confirmProjectCreation, setCreationStage }) => {
    const [files, setFiles] = useState([]);
    const [isDragging, setIsDragging] = useState(false);
    const [isCreating, setIsCreating] = useState(false);
    const [error, setError] = useState(null);
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
        if (droppedFiles.length > 0) addFiles(droppedFiles);
    };

    const handleFileSelect = (e) => {
        if (e.target.files) {
            const selectedFiles = Array.from(e.target.files);
            if (selectedFiles.length > 0) addFiles(selectedFiles);
        }
    };

    const addFiles = (newFiles) => {
        const fileEntries = newFiles.map(file => ({
            file: file, // Keep actual file object for upload
            name: file.name,
            size: (file.size / 1024 / 1024).toFixed(2),
            status: 'ready'
        }));
        setFiles(prev => [...prev, ...fileEntries]);
    };

    const handleContinue = async () => {
        setIsCreating(true);
        setError(null);
        
        try {
            // First, create the project
            const newProject = await confirmProjectCreation();
            
            // Then upload any files
            if (files.length > 0) {
                for (const fileEntry of files) {
                    try {
                        setFiles(prev => prev.map(f => 
                            f.name === fileEntry.name ? { ...f, status: 'uploading' } : f
                        ));
                        await uploadFile(newProject.id, fileEntry.file);
                        setFiles(prev => prev.map(f => 
                            f.name === fileEntry.name ? { ...f, status: 'completed' } : f
                        ));
                    } catch (err) {
                        setFiles(prev => prev.map(f => 
                            f.name === fileEntry.name ? { ...f, status: 'error' } : f
                        ));
                        console.error('File upload failed:', err);
                    }
                }
            }
            
            // Navigate to dashboard (handled in context)
        } catch (err) {
            console.error('Project creation failed:', err);
            setError('Failed to create project. Please ensure the backend is running.');
            setIsCreating(false);
        }
    };

    const handleSkip = async () => {
        setIsCreating(true);
        setError(null);
        
        try {
            await confirmProjectCreation();
        } catch (err) {
            console.error('Project creation failed:', err);
            setError('Failed to create project. Please ensure the backend is running.');
            setIsCreating(false);
        }
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

            {error && (
                <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
                    ⚠️ {error}
                </div>
            )}

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
                    accept=".pdf,.docx,.txt"
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
                                    <h4 className="text-sm font-medium text-gray-800 truncate max-w-[200px]">{file.name}</h4>
                                    <span className="text-xs text-gray-500">{file.size} MB</span>
                                </div>
                            </div>
                            <div className="ml-4">
                                {file.status === 'ready' && (
                                    <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600">Ready</span>
                                )}
                                {file.status === 'uploading' && (
                                    <span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-600 animate-pulse">Uploading...</span>
                                )}
                                {file.status === 'completed' && (
                                    <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-600">✓ Done</span>
                                )}
                                {file.status === 'error' && (
                                    <span className="text-xs px-2 py-1 rounded-full bg-red-100 text-red-600">✗ Failed</span>
                                )}
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>

            <div className="flex justify-between items-center border-t border-gray-100 pt-6">
                <button 
                    onClick={handleSkip}
                    disabled={isCreating}
                    className="text-gray-400 text-sm hover:text-gray-600 transition-colors disabled:opacity-50"
                >
                    Skip for now
                </button>
                <button
                    onClick={handleContinue}
                    disabled={files.length === 0 || isCreating}
                    className={`btn-primary flex items-center gap-2 min-w-[160px] justify-center ${
                        files.length === 0 ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                >
                    {isCreating ? (
                        <>
                            <span className="animate-spin">⚙️</span> Creating...
                        </>
                    ) : (
                        <>
                            Create Project <span>✨</span>
                        </>
                    )}
                </button>
            </div>
        </motion.div>
    );
};

export default OnboardingFlow;
