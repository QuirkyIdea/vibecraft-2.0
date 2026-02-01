"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { motion } from "framer-motion";
import { Loader2, CheckCircle, XCircle } from "lucide-react";
import styles from "./page.module.css";

function AuthCallbackContent() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const { handleAuthCallback } = useAuth();
    const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
    const [message, setMessage] = useState("Processing authentication...");

    useEffect(() => {
        const processAuth = async () => {
            const code = searchParams.get("code");
            const error = searchParams.get("error");

            if (error) {
                setStatus("error");
                setMessage("Authentication was cancelled or failed.");
                setTimeout(() => router.push("/"), 3000);
                return;
            }

            if (!code) {
                setStatus("error");
                setMessage("No authorization code received.");
                setTimeout(() => router.push("/"), 3000);
                return;
            }

            try {
                const success = await handleAuthCallback(code);
                if (success) {
                    setStatus("success");
                    setMessage("Authentication successful! Redirecting...");
                    setTimeout(() => router.push("/"), 1500);
                } else {
                    setStatus("error");
                    setMessage("Authentication failed. Please try again.");
                    setTimeout(() => router.push("/"), 3000);
                }
            } catch (err) {
                setStatus("error");
                setMessage("An error occurred during authentication.");
                setTimeout(() => router.push("/"), 3000);
            }
        };

        processAuth();
    }, [searchParams, handleAuthCallback, router]);

    return (
        <div className={styles.container}>
            <motion.div
                className={styles.card}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
            >
                {status === "loading" && (
                    <>
                        <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        >
                            <Loader2 size={48} className={styles.iconLoading} />
                        </motion.div>
                        <h2>Authenticating</h2>
                        <p>{message}</p>
                    </>
                )}

                {status === "success" && (
                    <>
                        <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ type: "spring", stiffness: 200 }}
                        >
                            <CheckCircle size={48} className={styles.iconSuccess} />
                        </motion.div>
                        <h2>Welcome!</h2>
                        <p>{message}</p>
                    </>
                )}

                {status === "error" && (
                    <>
                        <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ type: "spring", stiffness: 200 }}
                        >
                            <XCircle size={48} className={styles.iconError} />
                        </motion.div>
                        <h2>Authentication Failed</h2>
                        <p>{message}</p>
                    </>
                )}
            </motion.div>
        </div>
    );
}

export default function AuthCallback() {
    return (
        <Suspense fallback={
            <div className={styles.container}>
                <motion.div
                    className={styles.card}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3 }}
                >
                    <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    >
                        <Loader2 size={48} className={styles.iconLoading} />
                    </motion.div>
                    <h2>Loading</h2>
                    <p>Please wait...</p>
                </motion.div>
            </div>
        }>
            <AuthCallbackContent />
        </Suspense>
    );
}
