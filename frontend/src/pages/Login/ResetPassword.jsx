
import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { FaEye, FaEyeSlash } from "react-icons/fa";
import { toast } from "react-toastify";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/auth";

export default function ResetPassword() {
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const location = useLocation();
  const navigate = useNavigate();

  const phoneNumber = location.state?.phoneNumber;

  useEffect(() => {
    if (!phoneNumber) {
      navigate("/forgot-password", { replace: true });
    }
  }, [phoneNumber, navigate]);

  const resetPassword = async (e) => {
    e.preventDefault();
    setError("");

    if (!newPassword || newPassword.length < 8) {
      alert("Password must be at least 6 characters");
      return;
    }

    if (newPassword !== confirmPassword) {
      alert("Passwords do not match");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/password/reset/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          phoneNumber,
          newPassword,
          confirmPassword,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.message || "Reset failed");
      }

      toast.success("Password reset successfully!");

      setTimeout(() => {
        navigate("/login", { replace: true });
      }, 1200);
    } catch (error) {
      alert(error.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrapper--reset-page">
      <div className="auth-container--reset-card">
        <h2>Reset Password</h2>

        {error && <p className="reset-error">{error}</p>}
        {success && <p className="reset-success">{success}</p>}

        <form onSubmit={resetPassword} className="reset-form">

          <div className="password-field" style={{ position: "relative" }}>
            <input type={showNewPassword ? "text" : "password"} id="newPassword" name="newPassword" autoComplete="new-password" placeholder="New Password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} required />
            
            <span onClick={() => setShowNewPassword((prev) => !prev)} className="password-toggle" style={{ position: "absolute", right: "20px", top: "40%", transform: "translateY(-50%)", cursor: "pointer" }}>
              {showNewPassword ? <FaEyeSlash /> : <FaEye />}
            </span>
          </div>

          <div className="password-field" style={{ position: "relative" }}>
            <input type={showConfirmPassword ? "text" : "password"} id="confirmPassword" name="confirmPassword" autoComplete="new-password" placeholder="Confirm Password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required />
            <span
              onClick={() => setShowConfirmPassword((prev) => !prev)}
              style={{
                position: "absolute",
                right: "20px",
                top: "40%",
                transform: "translateY(-50%)",
                cursor: "pointer",
                }}>
                {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
            </span>
          </div>

          <button type="submit" disabled={loading} style={{ opacity: loading ? 0.6 : 1 }}>
            {loading ? "Resetting..." : "Reset Password"}
          </button>
        </form>
      </div>
    </div>
  );
}