"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    X,
    FileSearch,
    BookOpen,
    ArrowRight,
    ArrowLeft,
    Upload,
    FileText,
    Loader2,
    CheckCircle,
    Sparkles
} from "lucide-react";
import { useProjects, ProjectType } from "@/context/ProjectContext";
import styles from "./ProjectWizard.module.css";

interface ProjectWizardProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess?: (projectId: string) => void;
}

type WizardStep = "type" | "details" | "document" | "creating";

export default function ProjectWizard({ isOpen, onClose, onSuccess }: ProjectWizardProps) {
    const { createProject } = useProjects();
    const [step, setStep] = useState<WizardStep>("type");
    const [projectType, setProjectType] = useState<ProjectType | null>(null);
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [documentText, setDocumentText] = useState("");
    const [isCreating, setIsCreating] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const resetForm = () => {
        setStep("type");
        setProjectType(null);
        setTitle("");
        setDescription("");
        setDocumentText("");
        setError(null);
    };

    const handleClose = () => {
        resetForm();
        onClose();
    };

    const handleTypeSelect = (type: ProjectType) => {
        setProjectType(type);
        setStep("details");
    };

    const handleDetailsNext = () => {
        if (!title.trim()) {
            setError("Please enter a project title");
            return;
        }
        if (!description.trim()) {
            setError("Please enter a description");
            return;
        }
        setError(null);
        setStep("document");
    };

    const handleCreate = async () => {
        if (!projectType) return;

        setIsCreating(true);
        setStep("creating");
        setError(null);

        try {
            const project = await createProject({
                title: title.trim(),
                description: description.trim(),
                project_type: projectType,
                document_text: documentText.trim() || undefined
            });

            if (project) {
                setTimeout(() => {
                    handleClose();
                    if (onSuccess) {
                        onSuccess(project.id);
                    }
                }, 1500);
            } else {
                setError("Failed to create project");
                setStep("document");
            }
        } catch (err) {
            setError("An error occurred while creating the project");
            setStep("document");
        } finally {
            setIsCreating(false);
        }
    };

    const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        // For now, read text files directly
        if (file.type === "text/plain") {
            const reader = new FileReader();
            reader.onload = (e) => {
                setDocumentText(e.target?.result as string);
            };
            reader.readAsText(file);
        } else {
            // For PDF, we'll need to use the backend upload endpoint
            const formData = new FormData();
            formData.append("file", file);

            try {
                const response = await fetch(
                    `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/upload/pdf`,
                    { method: "POST", body: formData }
                );
                if (response.ok) {
                    const data = await response.json();
                    setDocumentText(data.text || "");
                }
            } catch (err) {
                console.error("File upload error:", err);
            }
        }
    };

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <motion.div
                className={styles.overlay}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={handleClose}
            >
                <motion.div
                    className={styles.modal}
                    initial={{ opacity: 0, scale: 0.95, y: 20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: 20 }}
                    onClick={(e) => e.stopPropagation()}
                >
                    {/* Header */}
                    <div className={styles.header}>
                        <div className={styles.headerContent}>
                            <Sparkles size={24} className={styles.headerIcon} />
                            <div>
                                <h2>Create New Project</h2>
                                <p>Start your innovation journey</p>
                            </div>
                        </div>
                        <button className={styles.closeButton} onClick={handleClose}>
                            <X size={20} />
                        </button>
                    </div>

                    {/* Progress Indicator */}
                    <div className={styles.progress}>
                        <div className={`${styles.step} ${step !== "type" ? styles.completed : styles.active}`}>
                            <span>1</span>
                            <p>Type</p>
                        </div>
                        <div className={styles.progressLine} />
                        <div className={`${styles.step} ${step === "details" ? styles.active : step === "document" || step === "creating" ? styles.completed : ""}`}>
                            <span>2</span>
                            <p>Details</p>
                        </div>
                        <div className={styles.progressLine} />
                        <div className={`${styles.step} ${step === "document" ? styles.active : step === "creating" ? styles.completed : ""}`}>
                            <span>3</span>
                            <p>Document</p>
                        </div>
                    </div>

                    {/* Content */}
                    <div className={styles.content}>
                        <AnimatePresence mode="wait">
                            {/* Step 1: Project Type */}
                            {step === "type" && (
                                <motion.div
                                    key="type"
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -20 }}
                                    className={styles.typeStep}
                                >
                                    <h3>What type of project?</h3>
                                    <div className={styles.typeGrid}>
                                        <motion.button
                                            className={styles.typeCard}
                                            onClick={() => handleTypeSelect("patent")}
                                            whileHover={{ scale: 1.02 }}
                                            whileTap={{ scale: 0.98 }}
                                        >
                                            <div className={styles.typeIcon} style={{ background: "linear-gradient(135deg, #6366f1, #8b5cf6)" }}>
                                                <FileSearch size={28} />
                                            </div>
                                            <h4>Patent Project</h4>
                                            <p>Analyze patent claims, assess novelty risks, and track filing progress</p>
                                            <ul className={styles.typeFeatures}>
                                                <li>Novelty Scanner</li>
                                                <li>Claim Analyzer</li>
                                                <li>Risk Indicators</li>
                                                <li>Filing Roadmap</li>
                                            </ul>
                                        </motion.button>

                                        <motion.button
                                            className={styles.typeCard}
                                            onClick={() => handleTypeSelect("research")}
                                            whileHover={{ scale: 1.02 }}
                                            whileTap={{ scale: 0.98 }}
                                        >
                                            <div className={styles.typeIcon} style={{ background: "linear-gradient(135deg, #06b6d4, #14b8a6)" }}>
                                                <BookOpen size={28} />
                                            </div>
                                            <h4>Research Project</h4>
                                            <p>Literature analysis, gap detection, and publication readiness tracking</p>
                                            <ul className={styles.typeFeatures}>
                                                <li>Literature Search</li>
                                                <li>Gap Detection</li>
                                                <li>Methodology Helper</li>
                                                <li>Publication Roadmap</li>
                                            </ul>
                                        </motion.button>
                                    </div>
                                </motion.div>
                            )}

                            {/* Step 2: Details */}
                            {step === "details" && (
                                <motion.div
                                    key="details"
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -20 }}
                                    className={styles.detailsStep}
                                >
                                    <h3>Project Details</h3>

                                    <div className={styles.formGroup}>
                                        <label htmlFor="title">Project Title</label>
                                        <input
                                            id="title"
                                            type="text"
                                            value={title}
                                            onChange={(e) => setTitle(e.target.value)}
                                            placeholder={projectType === "patent" ? "e.g., Smart Energy Grid Controller" : "e.g., AI-Powered Climate Prediction Model"}
                                            className={styles.input}
                                            maxLength={200}
                                        />
                                    </div>

                                    <div className={styles.formGroup}>
                                        <label htmlFor="description">Description</label>
                                        <textarea
                                            id="description"
                                            value={description}
                                            onChange={(e) => setDescription(e.target.value)}
                                            placeholder="Describe your idea, invention, or research focus..."
                                            className={styles.textarea}
                                            rows={5}
                                            maxLength={2000}
                                        />
                                        <span className={styles.charCount}>{description.length}/2000</span>
                                    </div>

                                    {error && <p className={styles.error}>{error}</p>}

                                    <div className={styles.actions}>
                                        <button className={styles.backButton} onClick={() => setStep("type")}>
                                            <ArrowLeft size={18} />
                                            Back
                                        </button>
                                        <button className={styles.nextButton} onClick={handleDetailsNext}>
                                            Continue
                                            <ArrowRight size={18} />
                                        </button>
                                    </div>
                                </motion.div>
                            )}

                            {/* Step 3: Document */}
                            {step === "document" && (
                                <motion.div
                                    key="document"
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -20 }}
                                    className={styles.documentStep}
                                >
                                    <h3>Add Document (Optional)</h3>
                                    <p className={styles.stepDescription}>
                                        Upload a document or paste text for deeper analysis
                                    </p>

                                    <div className={styles.uploadArea}>
                                        <input
                                            type="file"
                                            id="fileUpload"
                                            accept=".pdf,.txt,.docx"
                                            onChange={handleFileUpload}
                                            className={styles.fileInput}
                                        />
                                        <label htmlFor="fileUpload" className={styles.uploadLabel}>
                                            <Upload size={32} />
                                            <span>Drop file here or click to upload</span>
                                            <small>PDF, TXT, or DOCX (max 10MB)</small>
                                        </label>
                                    </div>

                                    <div className={styles.orDivider}>
                                        <span>or paste text directly</span>
                                    </div>

                                    <textarea
                                        value={documentText}
                                        onChange={(e) => setDocumentText(e.target.value)}
                                        placeholder="Paste your document content, patent claims, or research abstract here..."
                                        className={styles.documentTextarea}
                                        rows={6}
                                    />

                                    {documentText && (
                                        <div className={styles.documentInfo}>
                                            <FileText size={16} />
                                            <span>{documentText.length.toLocaleString()} characters</span>
                                        </div>
                                    )}

                                    {error && <p className={styles.error}>{error}</p>}

                                    <div className={styles.actions}>
                                        <button className={styles.backButton} onClick={() => setStep("details")}>
                                            <ArrowLeft size={18} />
                                            Back
                                        </button>
                                        <button className={styles.createButton} onClick={handleCreate}>
                                            Create Project
                                            <Sparkles size={18} />
                                        </button>
                                    </div>
                                </motion.div>
                            )}

                            {/* Step 4: Creating */}
                            {step === "creating" && (
                                <motion.div
                                    key="creating"
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    className={styles.creatingStep}
                                >
                                    {isCreating ? (
                                        <>
                                            <motion.div
                                                animate={{ rotate: 360 }}
                                                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                            >
                                                <Loader2 size={48} className={styles.loadingIcon} />
                                            </motion.div>
                                            <h3>Creating Your Project</h3>
                                            <p>Setting up workspace and generating roadmap...</p>
                                        </>
                                    ) : (
                                        <>
                                            <motion.div
                                                initial={{ scale: 0 }}
                                                animate={{ scale: 1 }}
                                                transition={{ type: "spring", stiffness: 200 }}
                                            >
                                                <CheckCircle size={48} className={styles.successIcon} />
                                            </motion.div>
                                            <h3>Project Created!</h3>
                                            <p>Redirecting to your project...</p>
                                        </>
                                    )}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
}
