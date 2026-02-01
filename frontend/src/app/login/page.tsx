"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Zap, Shield, Brain, ArrowRight } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import styles from "./page.module.css";

export default function LoginPage() {
    const { isAuthenticated, isLoading, login } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!isLoading && isAuthenticated) {
            router.push("/");
        }
    }, [isAuthenticated, isLoading, router]);

    if (isLoading) {
        return (
            <div className={styles.loadingContainer}>
                <motion.div
                    className={styles.loadingOrb}
                    animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 2, repeat: Infinity }}
                />
            </div>
        );
    }

    return (
        <div className={styles.container}>
            {/* Background Effects */}
            <div className={styles.backgroundEffects}>
                <motion.div
                    className={styles.gradientOrb1}
                    animate={{ x: [0, 100, 0], y: [0, -50, 0] }}
                    transition={{ duration: 20, repeat: Infinity }}
                />
                <motion.div
                    className={styles.gradientOrb2}
                    animate={{ x: [0, -80, 0], y: [0, 80, 0] }}
                    transition={{ duration: 15, repeat: Infinity }}
                />
            </div>

            <div className={styles.content}>
                {/* Hero Section */}
                <motion.div
                    className={styles.hero}
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                >
                    <div className={styles.logo}>
                        <motion.div
                            className={styles.logoIcon}
                            animate={{ rotate: [0, 5, -5, 0] }}
                            transition={{ duration: 4, repeat: Infinity }}
                        >
                            <Zap size={40} />
                        </motion.div>
                        <span className={styles.logoText}>Inventix AI</span>
                    </div>

                    <h1 className={styles.title}>
                        Evidence-Locked
                        <br />
                        <span className={styles.highlight}>Research Intelligence</span>
                    </h1>

                    <p className={styles.description}>
                        ANTIGRAVITY is your constrained intelligence companion for research and patent analysis.
                        Transform ideas into evidence-backed insights with probabilistic precision.
                    </p>

                    <motion.button
                        className={styles.loginButton}
                        onClick={login}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                    >
                        <svg className={styles.googleIcon} viewBox="0 0 24 24" width="20" height="20">
                            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                        </svg>
                        <span>Continue with Google</span>
                        <ArrowRight size={18} />
                    </motion.button>
                </motion.div>

                {/* Features */}
                <motion.div
                    className={styles.features}
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                >
                    <div className={styles.feature}>
                        <div className={styles.featureIcon}>
                            <Brain size={24} />
                        </div>
                        <div className={styles.featureContent}>
                            <h3>Patent Intelligence</h3>
                            <p>Novelty scanning, claim analysis, and risk indicators</p>
                        </div>
                    </div>

                    <div className={styles.feature}>
                        <div className={styles.featureIcon}>
                            <Shield size={24} />
                        </div>
                        <div className={styles.featureContent}>
                            <h3>Research Engine</h3>
                            <p>Literature search, gap detection, methodology suggestions</p>
                        </div>
                    </div>

                    <div className={styles.feature}>
                        <div className={styles.featureIcon}>
                            <Zap size={24} />
                        </div>
                        <div className={styles.featureContent}>
                            <h3>Evidence-Locked</h3>
                            <p>Every output is grounded, referenced, and auditable</p>
                        </div>
                    </div>
                </motion.div>

                {/* System Boundaries */}
                <motion.div
                    className={styles.disclaimer}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.6, delay: 0.4 }}
                >
                    <p>
                        <strong>System Boundaries:</strong> All outputs are probabilistic estimates.
                        This system does not provide legal advice or determine patentability.
                    </p>
                </motion.div>
            </div>
        </div>
    );
}
