"use client";

import { motion } from "framer-motion";
import { Activity, Shield, Zap, LogIn, LogOut, User } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import styles from "./Header.module.css";

export default function Header() {
    const { user, isAuthenticated, login, logout, isLoading } = useAuth();

    return (
        <header className={styles.header}>
            <div className={styles.container}>
                <div className={styles.logoSection}>
                    <motion.div
                        className={styles.logoIcon}
                        animate={{
                            boxShadow: [
                                "0 0 20px rgba(99, 102, 241, 0.3)",
                                "0 0 40px rgba(99, 102, 241, 0.5)",
                                "0 0 20px rgba(99, 102, 241, 0.3)",
                            ],
                        }}
                        transition={{ duration: 2, repeat: Infinity }}
                    >
                        <Zap size={24} />
                    </motion.div>
                    <div className={styles.logoText}>
                        <span className={styles.logoTitle}>INVENTIX</span>
                        <span className={styles.logoSubtitle}>AI</span>
                    </div>
                </div>

                <div className={styles.centerSection}>
                    <div className={styles.systemBadge}>
                        <Shield size={14} />
                        <span>ANTIGRAVITY</span>
                    </div>
                    <span className={styles.modeBadge}>Evidence-Locked Mode</span>
                </div>

                <div className={styles.rightSection}>
                    <div className={styles.statusIndicator}>
                        <motion.div
                            className={styles.statusDot}
                            animate={{ scale: [1, 1.2, 1] }}
                            transition={{ duration: 2, repeat: Infinity }}
                        />
                        <span>System Operational</span>
                    </div>

                    {isLoading ? (
                        <div className={styles.userSkeleton} />
                    ) : isAuthenticated && user ? (
                        <div className={styles.userSection}>
                            {user.picture ? (
                                <img
                                    src={user.picture}
                                    alt={user.name}
                                    className={styles.userAvatar}
                                />
                            ) : (
                                <div className={styles.userAvatarPlaceholder}>
                                    <User size={16} />
                                </div>
                            )}
                            <span className={styles.userName}>{user.name?.split(" ")[0]}</span>
                            <button
                                className={styles.logoutButton}
                                onClick={logout}
                                title="Sign out"
                            >
                                <LogOut size={16} />
                            </button>
                        </div>
                    ) : (
                        <motion.button
                            className={styles.loginButton}
                            onClick={login}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                        >
                            <LogIn size={16} />
                            <span>Sign In</span>
                        </motion.button>
                    )}
                </div>
            </div>
        </header>
    );
}

