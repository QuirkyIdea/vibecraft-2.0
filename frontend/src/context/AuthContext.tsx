"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from "react";

interface User {
    id: string;
    email: string;
    name: string;
    picture?: string;
    created_at: string;
}

interface AuthContextType {
    user: User | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    login: () => void;
    logout: () => void;
    handleAuthCallback: (code: string) => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = "inventix_token";
const USER_KEY = "inventix_user";
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Check for existing session on mount
    useEffect(() => {
        const checkAuth = async () => {
            const token = localStorage.getItem(TOKEN_KEY);
            const storedUser = localStorage.getItem(USER_KEY);

            if (token && storedUser) {
                try {
                    // Verify token is still valid
                    const response = await fetch(`${API_URL}/api/auth/verify`, {
                        headers: {
                            Authorization: `Bearer ${token}`
                        }
                    });

                    if (response.ok) {
                        setUser(JSON.parse(storedUser));
                    } else {
                        // Token expired, clear storage
                        localStorage.removeItem(TOKEN_KEY);
                        localStorage.removeItem(USER_KEY);
                    }
                } catch (error) {
                    console.error("Auth check failed:", error);
                }
            }
            setIsLoading(false);
        };

        checkAuth();
    }, []);

    const login = useCallback(async () => {
        try {
            // Get Google OAuth URL from backend
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

            const response = await fetch(`${API_URL}/api/auth/google/url`, {
                signal: controller.signal
            });
            clearTimeout(timeoutId);

            const data = await response.json();

            if (data.url) {
                // Redirect to Google OAuth
                window.location.href = data.url;
            } else if (data.client_id) {
                // Build OAuth URL manually if only client_id is provided
                const params = new URLSearchParams({
                    client_id: data.client_id,
                    redirect_uri: `${window.location.origin}/auth/callback`,
                    response_type: "code",
                    scope: "openid email profile",
                    access_type: "offline",
                    prompt: "consent"
                });
                window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?${params}`;
            }
        } catch (error) {
            console.error("Login error, using fallback:", error);
            // Fallback: Try to build URL with known client_id
            const clientId = "832754819153-uph75gvuhedsqnmhrfkqghtdfn8hoiei.apps.googleusercontent.com";
            const params = new URLSearchParams({
                client_id: clientId,
                redirect_uri: `${window.location.origin}/auth/callback`,
                response_type: "code",
                scope: "openid email profile",
                access_type: "offline",
                prompt: "consent"
            });
            window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?${params}`;
        }
    }, []);

    const handleAuthCallback = useCallback(async (code: string): Promise<boolean> => {
        try {
            const response = await fetch(`${API_URL}/api/auth/google/callback`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    code,
                    redirect_uri: `${window.location.origin}/auth/callback`
                })
            });

            if (!response.ok) {
                throw new Error("Authentication failed");
            }

            const data = await response.json();

            // Store token and user
            localStorage.setItem(TOKEN_KEY, data.access_token);
            localStorage.setItem(USER_KEY, JSON.stringify(data.user));
            setUser(data.user);

            return true;
        } catch (error) {
            console.error("Auth callback error:", error);
            return false;
        }
    }, []);

    const logout = useCallback(async () => {
        try {
            const token = localStorage.getItem(TOKEN_KEY);
            if (token) {
                await fetch(`${API_URL}/api/auth/logout`, {
                    method: "POST",
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
            }
        } catch (error) {
            console.error("Logout error:", error);
        } finally {
            localStorage.removeItem(TOKEN_KEY);
            localStorage.removeItem(USER_KEY);
            setUser(null);
        }
    }, []);

    return (
        <AuthContext.Provider
            value={{
                user,
                isLoading,
                isAuthenticated: !!user,
                login,
                logout,
                handleAuthCallback
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}

// Helper to get auth token for API calls
export function getAuthToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(TOKEN_KEY);
}

// Helper for authenticated fetch
export async function authFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const token = getAuthToken();
    const headers = new Headers(options.headers);

    if (token) {
        headers.set("Authorization", `Bearer ${token}`);
    }

    return fetch(url, {
        ...options,
        headers
    });
}
