import React, { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext();

const AUTH_API =
    import.meta.env.VITE_AUTH_API || "http://127.0.0.1:8000/api/auth";

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    // ------------------ Fetch User ------------------ //
    const fetchUser = async (isInitial = false) => {
        if (isInitial) setLoading(true);

        try {
            // const res = await fetch(`${API_BASE}/user/me/`, {
            const res = await fetch(`${AUTH_API}/session/`, {
                method: "GET",
                credentials: "include",
            });

            if (res.status === 401) {
                setUser(null);
                return false;
            }

            if (!res.ok) {
                setUser(null);
                return false;
            }

            const data = await res.json();

            if (data.authenticated && data.user) {
                setUser(data.user);
                return true;
            }
            
            setUser(null);
            return false;
        } catch (err) {
            console.error("Auth error:", err);
            setUser(null);
            return false;
        } finally {
            // if (isInitial) setLoading(false);
            setLoading(false);
        }
    };

    // Run on app load
    useEffect(() => {
        fetchUser(true);
    }, []);

    // ------------------ Login ------------------ //
    const login = async (username, password) => {
        try {
            const res = await fetch(`${AUTH_API}/login/`, {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ username, password }),
            });

            const data = await res.json();

            if (!res.ok) {
                return {
                    success: false,
                    status: res.status,
                    message: data.error || "Login failed",
                };
            }

            if (data.success === false) {
                return {
                    success: false,
                    status: 401,
                    message: data.error || "Invalid email or password",
                };
            }

            await fetchUser(false);

            return {
                success: true,
                message: data.message || "Login successful",
            };
        } catch (err) {
            return {
                success: false,
                message: err.message || "Something went wrong",
            };
        }
    };

    // ------------------ Google Login ------------------ //
    const googleLogin = async (credential) => {
        try {
            const res = await fetch(`${API_BASE}/google-login/`, {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ credential }),
            });

            const data = await res.json();

            if (!res.ok) {
                return {
                    success: false,
                    status: res.status,
                    message: data.error || "Google login failed",
                };
            }

            await fetchUser(false);

            return {
                success: true,
                message: data.message || "Google login successful",
            };
        } catch (err) {
            return {
                success: false,
                message: err.message || "Something went wrong",
            };
        }
    };

    // ------------------ Signup ------------------ //
    const signup = async (payload) => {
        try {
            const res = await fetch(`${AUTH_API}/signup/`, {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            const contentType = res.headers.get("content-type") || "";
            let data = {};

            if (contentType.includes("application/json")) {
                data = await res.json();
            } else {
                const text = await res.text();
                console.error("Signup non-JSON response:", text);

                return {
                    success: false,
                    status: res.status,
                    message: "Server returned invalid response",
                };
            }

            // const data = await res.json();

            if (!res.ok) {
                return {
                    success: false,
                    status: res.status,
                    errors: data.errors || null,
                    message: data.error || data.message || "Signup failed",
                };
            }

            return {
                success: true,
                message: data.message || "Account created successfully",
            };
        } catch (err) {
            return {
                success: false,
                message: err.message || "Something went wrong",
            };
        }
    };

    // ------------------ Logout ------------------ //
    const logout = async () => {
        try {
            const res = await fetch(`${AUTH_API}/logout/`, {
                method: "POST",
                credentials: "include",
                 headers: {
                    "Content-Type": "application/json",
                 },
            });

            if (res.status === 401) {
                setUser(null);
                return {
                    success: true,
                    message: "Session already expired",
                };
            }

            let data = {};
            try {
                data = await res.json();
            } catch {
                data = {};
            }

            if (!res.ok) {
                return {
                    success: false,
                    status: res.status,
                    message: data.error || data.message || "Logout failed",
                };
            }

            setUser(null);

            return {
                success: true,
                message: data.message || "Logout successful",
            };
        } catch (error) {
            return {
                success: false,
                message: error.message || "Network error during logout",
            };
        }
    };

    // ------------------ Update Profile ------------------ //
    const updateProfile = async (formData) => {
        try {
            const res = await fetch(`${AUTH_API}/user/profile/update/`, {
                method: "PUT",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(formData),
            });

            const contentType = res.headers.get("content-type") || "";
            let data = {};

            if (contentType.includes("application/json")) {
                data = await res.json();
            } else {
                const text = await res.text();
                console.error("Non-JSON response from backend:", text);
                return {
                    success: false,
                    message: "Server error: backend did not return valid JSON.",
                    errors: {},
                };
            }

            // const data = await res.json();

            if (!res.ok) {
                return {
                    success: false,
                    message: data.error || data.message || "Profile update failed",
                    errors: data.errors || {},
                };
            }

            setUser((prev) => ({
                ...prev,
                ...data.user,
            }));

            return {
                success: true,
                message: data.message || "Profile updated successfully",
                data: data.user,
            };
        } catch (error) {
            console.error("Update error:", error);
            return {
                success: false,
                message: error.message || "Something went wrong",
                errors: {},
            };
        }
    };

    return (
        <AuthContext.Provider
            value={{ user, isLoggedIn: !!user, loading, login, googleLogin, signup, logout, updateProfile, fetchUser, }}>
                {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);

    if (!context) {
        throw new Error("useAuth must be used inside AuthProvider");
    }

    return context;
};