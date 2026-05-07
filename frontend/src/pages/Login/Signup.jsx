import React, { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import logo from "../../assets/image/logo/vastrika-logo.png";
import { updateMeta, updateOG } from "../../utils/updateOG";
import { FaEye, FaEyeSlash } from "react-icons/fa";
import { toast } from "react-toastify";
import { useAuth } from "../../context/AuthContext";
import PasswordStrength from "../../components/auth/PasswordStrength"; // Password Strength
import zxcvbn from "zxcvbn";

export default function Signup() {
  const navigate = useNavigate();
  const { signup } = useAuth();

  useEffect(() => {
    updateMeta({
      title: "Sign Up | Vastrika Fashion Store",
      description:
        "Create your Vastrika account to shop, track orders, and enjoy personalized fashion.",
    });

    updateOG({
      title: "Sign Up | Vastrika Fashion Store",
      description:
        "Create your Vastrika account to shop, track orders, and enjoy personalized fashion.",
      image: window.location.origin + "/assets/image/logo/vastrika-logo.png",
      url: window.location.origin + "/",
    });
  }, []);

  // ------------------ STATES ------------------ //
  const [form, setForm] = useState({
    name: "",
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  // ------------------ VALIDATION ------------------ //
  const validate = () => {
    const newErrors = {};

    if (!form.name.trim()) {
      newErrors.name = "Name is required";
    }

    if (!form.username.trim()) {
      newErrors.username = "Username is required";
    }

    if (!form.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) {
      newErrors.email = "Invalid email format";
    }

    if (!form.password) {
      newErrors.password = "Password is required";
    } else if (form.password.length < 10) {
      newErrors.password = "Minimum 10 characters required";
    } else if (zxcvbn(form.password, [form.email, form.name]).score < 2) {
      newErrors.password = "Please choose a stronger password";
    }

    if (!form.confirmPassword) {
      newErrors.confirmPassword = "Please confirm password";
    } else if (form.password !== form.confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }

    return newErrors;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));

    setErrors((prev) => ({
      ...prev,
      [name]: "",
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setLoading(true);

    try {
      const result = await signup({
        username: form.username.trim(),
        first_name: form.name.trim(),
        email: form.email.trim().toLowerCase(),
        password: form.password,
      });

      if (!result.success) {
        // if (result.errors) {
          const backendErrors = {};

          if (result.errors?.email?.[0]) {
            backendErrors.email = result.errors.email[0];
          }
          if (result.errors?.password?.[0]) {
            backendErrors.password = result.errors.password[0];
          }
          if (result.errors?.first_name?.[0]) {
            backendErrors.name = result.errors.first_name[0];
          }
          if (result.errors?.username?.[0]) {
            backendErrors.username = result.errors.username[0];
          }

          setErrors((prev) => ({ ...prev, ...backendErrors }));
        // }

        if (!backendErrors.email && !backendErrors.password && !backendErrors.name) {
          toast.error(result.message || "Signup failed");
        }
        
        return;
      }

      toast.success(result.message || "Account created successfully");
      setTimeout(() => navigate("/login"), 1200);

      setForm({
        name: "",
        username: "",
        email: "",
        password: "",
        confirmPassword: "",
      });
    } catch (error) {
      toast.error(error.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-layout">
      <div className="main-content">
        <div className="auth-wrapper--register__account">
          <div className="auth-container--register__account">
            <div className="auth-card--register__account">
              <Link to="/">
                <img src={logo} alt="Vastrika Logo" className="auth-logo--register__account" />
              </Link>

              <h1>Create Account</h1>

              <form onSubmit={handleSubmit}>
                <input id="name" name="name" value={form.name} onChange={handleChange} type="text" autoComplete="name" placeholder="Your Name" />
                {errors.name && (
                  <p className="error-text" style={{ marginTop: "-12px", fontSize: "12px", color: "#cf0e0e", }}>
                    <span>!</span> {errors.name}
                  </p>
                )}

                <input id="username" name="username" value={form.username} onChange={handleChange} type="text" autoComplete="username" placeholder="Username" />
                {errors.username && (
                  <p className="error-text" style={{ marginTop: "-12px", fontSize: "12px", color: "#cf0e0e" }}>
                    <span>!</span> {errors.username}
                  </p>
                )}

                <input id="email" name="email" value={form.email} onChange={handleChange} type="email" autoComplete="email" placeholder="Email Address" />
                {errors.email && (
                  <p className="error-text" style={{ marginTop: "-12px", fontSize: "12px", color: "#cf0e0e" }}>
                    <span>!</span> {errors.email}
                  </p>
                )}

                <div className="password-field" style={{ position: "relative" }}>
                  <input id="password" name="password" value={form.password} onChange={handleChange} type={showPassword ? "text" : "password"} autoComplete="new-password" placeholder="Password (min 10 characters)" />
                  <span onClick={() => setShowPassword(!showPassword)} style={{ position: "absolute", right: "20px", top: "40%", transform: "translateY(-50%)", cursor: "pointer" }}>
                    {showPassword ? <FaEyeSlash /> : <FaEye />}
                  </span>
                </div>
                <PasswordStrength password={form.password} email={form.email} name={form.name} />
                {errors.password && (
                  <p className="error-text" style={{ marginTop: "-12px", fontSize: "12px", color: "#cf0e0e" }}>
                    <span>!</span> {errors.password}
                  </p>
                )}

                <div className="password-field" style={{ position: "relative" }}>
                  <input
                    id="confirmPassword"
                    name="confirmPassword"
                    value={form.confirmPassword}
                    onChange={handleChange}
                    type={showConfirm ? "text" : "password"}
                    autoComplete="new-password"
                    placeholder="Confirm Password"
                  />
                  <span
                    onClick={() => setShowConfirm(!showConfirm)}
                    style={{
                      position: "absolute",
                      right: "20px",
                      top: "40%",
                      transform: "translateY(-50%)",
                      cursor: "pointer",
                    }}
                  >
                    {showConfirm ? <FaEyeSlash /> : <FaEye />}
                  </span>
                </div>
                {errors.confirmPassword && (
                  <p
                    className="error-text"
                    style={{
                      marginTop: "-12px",
                      fontSize: "12px",
                      color: "#cf0e0e",
                    }}
                  >
                    <span>!</span> {errors.confirmPassword}
                  </p>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="auth-btn--register__account"
                >
                  {loading ? "Creating..." : "Sign Up"}
                </button>
              </form>

              <p className="auth-info--register__account">
                By creating an account, you agree to Vastrika&apos;s <span>Terms</span> and{" "}
                <span>Privacy Policy</span>
              </p>

              <hr />

              <p className="auth-footer--register__account">
                Already have an account?{" "}
                <Link to="/login">
                  <span>Login</span>
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}