import React, { useEffect, useState } from "react";
import logo from "../../assets/image/logo/vastrika-white-logo.png";
import userLoginBanner from "../../assets/image/user-login-banner.png";
// import googleIcon from "../../assets/image/google-icon.png";
import { updateMeta, updateOG } from "../../utils/updateOG";
import { useNavigate, Link, useLocation } from "react-router-dom";
import { FaEye, FaEyeSlash } from "react-icons/fa";
import { useAuth } from "../../context/AuthContext";
import { toast } from "react-toastify"; // Toast Notification 
import GoogleLoginButton from "../../components/auth/GoogleLoginButton"; // Google Login

export default function Login() {
    const navigate = useNavigate();
    const location = useLocation();
    const { login } = useAuth();

    const redirectTo = location.state?.from?.pathname || "/";

    // ------------------ STATE ------------------ //
    const [email, setEmail] = useState("");
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [agreed, setAgreed] = useState(false); // State for checkbox

    const [errors, setErrors] = useState({});
    // const [serverError, setServerError] = useState("");

    const [showErrorModal, setShowErrorModal] = useState(false);
    const [modalMessage, setModalMessage] = useState("");

    useEffect(() => {
        updateMeta({
            title: "Login | Vastrika Fashion Store",
            description:
                "Login to your Vastrika account to manage orders, wishlist, and profile securely.",
        });

        updateOG({
            title: "Login | Vastrika Fashion Store",
            description:
                "Login to your Vastrika account for seamless shopping experience.",
            image: window.location.origin + "/assets/image/logo/vastrika-logo.png",
            url: window.location.origin + "/",
        });
    }, []);

    // ------------------ VALIDATION ------------------ //
    const validate = () => {
        const newErrors = {};

        if (!email.trim()) {
            newErrors.email = "Email is required";
        }

        if (!password.trim()) {
            newErrors.password = "Password is required";
        }

        if (!agreed) {
            newErrors.agreed("Please accept Terms & Policy");
            return false;
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

        const handleAgreeChange = (e) => {
        setAgreed(e.target.checked);
        if (errors.agreed) {
            setErrors((prev) => ({ ...prev, agreed: "" }));
        }
    };

    // ------------------ LOGIN (API connect) ------------------ //
    const handleLogin = async (e) => {
        e.preventDefault();
        // setServerError("");

        if (!validate()) {
            toast.error("Please fill all required fields");
            return;
        }

        setLoading(true);

        try {
            const result = await login(email.trim(), password);

            if (result.success) {
                toast.success(result.message || "Login successful");
                navigate(redirectTo, { replace: true });
                return;
            }

            // setServerError(result.message || "Login failed");

            if (result.status === 400) {
                toast.error(result.message || "Email and password are required");
            } else if (result.status === 401) {
                setModalMessage(
                    result.message || "Invalid email or password. Please try again."
                );

                setShowErrorModal(true);
                toast.error(result.message || "Invalid email or password");
            } else {
                toast.error(result.message || "Login failed");
            }
        } catch (error) {
            console.error("Login Error:", error);
            toast.error(error.message || "Something went wrong");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="app-layout">
            <div className="main-content">

                {/* user-login */}
                <div className="auth-wrapper">
                    <div className="auth-container">

                        {/* LEFT SIDE */}
                        <div className="auth-left">
                            <div className="user-logo">
                                <Link to="/">
                                    <img src={logo} alt="Vastrika Logo" />
                                </Link>
                            </div>

                            <p>
                                Create an account to unlock exclusive deals, new arrivals and
                                personalized recommendations.
                            </p>

                            <img src={userLoginBanner} alt="User login banner" className="login-banner" />
                        </div>

                        {/* RIGHT SIDE */}
                        <div className="auth-right">
                            <h2>Login</h2>

                            {/* {serverError && <p className="error-text">{serverError}</p>} */}

                            <form onSubmit={handleLogin} noValidate>
                                <input type="email" id="email" name="email" autoComplete="email" placeholder="Username" value={email} onChange={(e) => { setEmail(e.target.value);
                                if (errors.email) { setErrors((prev) => ({ ...prev, email: "" })); }}} />
                                {errors.email && (
                                    <p className="error-text" style={{ marginTop: "-12px", fontSize: "12px", color: "#cf0e0e" }}>
                                        <span>!</span> {errors.email}
                                    </p>
                                )}

                                <div className="password-field" style={{ position: "relative" }}>
                                    <input type={showPassword ? "text" : "password"} id="password" name="password" autoComplete="current-password" placeholder="Password" value={password} onChange={(e) => {
                                        setPassword(e.target.value);
                                        if (errors.password) {
                                            setErrors((prev) => ({ ...prev, password: "" }));
                                        }
                                    }} />

                                    <span onClick={() => setShowPassword(!showPassword)} className="password-toggle" style={{ position: "absolute", right: "20px", top: "40%", transform: "translateY(-50%)", cursor: "pointer" }}>
                                        {showPassword ? <FaEyeSlash /> : <FaEye />}
                                    </span>
                                </div>

                                {errors.password && (
                                    <p className="error-text" style={{ marginTop: "-12px", fontSize: "12px", color: "#cf0e0e" }}>
                                        <span>!</span> {errors.password}
                                    </p>
                                )}

                                {/* OPTIONS */}
                                <div className="options">
                                     <div className="account_login--remember position_relative">
                                         <input className="checkout_checkbox--input" type="checkbox" id="terms-checkbox"  checked={agreed} onChange={handleAgreeChange} />

                                         <label className="checkout_checkbox--label login_remember--label" htmlFor="terms-checkbox" style={{ cursor: 'pointer' }}>
                                             I agree to{" "}&nbsp;
                                             <Link to="/terms-and-conditions" style={{ color: '#c5396a' }}>Terms</Link>&nbsp; &{" "}&nbsp;
                                             <Link to="/privacy-policy" style={{ color: '#c5396a' }}>Privacy Policy</Link>
                                        </label>
                                     </div>

                                    <Link to="/forgot-password" className="forgot">
                                        Forgot Password?
                                    </Link>
                                </div>

                                {errors.agreed && (
                                    <p className="error-text">{errors.agreed}</p>
                                )}

                                <button type="submit" className="login-btn" disabled={loading || !agreed} style={{ opacity: (loading || !agreed) ? 0.6 : 1 }}>
                                    {loading ? "Logging in..." : "Login"}
                                </button>

                                {/* REGISTER */}
                                <div className="register--account">
                                    Don&apos;t have an account? <Link to="/signup">Create Account</Link>
                                </div>

                                <div className="divider">OR</div>

                                <div className="social-buttons">
                                    <GoogleLoginButton />
                                    {/* <button type="button" className="google">
                                        <img src={googleIcon} alt="Google" />
                                        &nbsp;Continue with Google
                                    </button> */}
                                </div>
                            </form>
                        </div>
                    </div>
                </div>

                {showErrorModal && (
                    <div className="login-modal-overlay">
                        <div className="login-modal-box">
                            <h3>Login Failed</h3>
                            <p>{modalMessage}</p>

                            <div className="login-modal-actions">
                                <button onClick={() => setShowErrorModal(false)} className="login-modal-btn secondary">Try Again</button>
                                <button onClick={() => navigate("/signup")} className="login-modal-btn primary">
                                    Create Account
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}