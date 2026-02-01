"use client";

import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, X, Loader2, Check, AlertCircle } from "lucide-react";
import styles from "./PDFUpload.module.css";

interface PDFUploadProps {
    onTextExtracted: (text: string, filename: string) => void;
    compact?: boolean;
}

interface UploadState {
    status: "idle" | "uploading" | "success" | "error";
    filename?: string;
    pageCount?: number;
    charCount?: number;
    error?: string;
}

export default function PDFUpload({ onTextExtracted, compact = false }: PDFUploadProps) {
    const [state, setState] = useState<UploadState>({ status: "idle" });
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFile = async (file: File) => {
        if (!file.name.toLowerCase().endsWith(".pdf")) {
            setState({
                status: "error",
                error: "Only PDF files are accepted",
            });
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            setState({
                status: "error",
                error: "File size exceeds 10MB limit",
            });
            return;
        }

        setState({ status: "uploading", filename: file.name });

        try {
            const formData = new FormData();
            formData.append("file", file);

            const response = await fetch("http://localhost:8000/api/upload/pdf", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (data.success) {
                setState({
                    status: "success",
                    filename: data.filename,
                    pageCount: data.page_count,
                    charCount: data.char_count,
                });
                onTextExtracted(data.text, data.filename);
            } else {
                setState({
                    status: "error",
                    filename: file.name,
                    error: data.error || "Failed to extract text from PDF",
                });
            }
        } catch (err) {
            setState({
                status: "error",
                filename: file.name,
                error: "Failed to upload file. Is the backend running?",
            });
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);

        const file = e.dataTransfer.files[0];
        if (file) {
            handleFile(file);
        }
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleClick = () => {
        fileInputRef.current?.click();
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            handleFile(file);
        }
    };

    const handleClear = () => {
        setState({ status: "idle" });
        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };

    return (
        <div className={`${styles.container} ${compact ? styles.compact : ""}`}>
            <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={handleInputChange}
                className={styles.hiddenInput}
            />

            <AnimatePresence mode="wait">
                {state.status === "idle" && (
                    <motion.div
                        key="idle"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className={`${styles.dropzone} ${isDragging ? styles.dragging : ""}`}
                        onClick={handleClick}
                        onDrop={handleDrop}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                    >
                        <Upload size={compact ? 20 : 32} className={styles.uploadIcon} />
                        <div className={styles.dropzoneText}>
                            <span className={styles.primary}>
                                {compact ? "Upload PDF" : "Drop PDF here or click to upload"}
                            </span>
                            {!compact && (
                                <span className={styles.secondary}>
                                    Max 10MB, up to 50 pages
                                </span>
                            )}
                        </div>
                    </motion.div>
                )}

                {state.status === "uploading" && (
                    <motion.div
                        key="uploading"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className={styles.statusBox}
                    >
                        <Loader2 size={20} className={styles.spinner} />
                        <span>Extracting text from {state.filename}...</span>
                    </motion.div>
                )}

                {state.status === "success" && (
                    <motion.div
                        key="success"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className={`${styles.statusBox} ${styles.success}`}
                    >
                        <div className={styles.statusContent}>
                            <FileText size={20} />
                            <div className={styles.fileInfo}>
                                <span className={styles.filename}>{state.filename}</span>
                                <span className={styles.meta}>
                                    {state.pageCount} pages | {state.charCount?.toLocaleString()} chars
                                </span>
                            </div>
                        </div>
                        <button onClick={handleClear} className={styles.clearBtn}>
                            <X size={16} />
                        </button>
                    </motion.div>
                )}

                {state.status === "error" && (
                    <motion.div
                        key="error"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className={`${styles.statusBox} ${styles.error}`}
                    >
                        <div className={styles.statusContent}>
                            <AlertCircle size={20} />
                            <span>{state.error}</span>
                        </div>
                        <button onClick={handleClear} className={styles.clearBtn}>
                            <X size={16} />
                        </button>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
