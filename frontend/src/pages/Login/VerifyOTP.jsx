import React, { useEffect, useState, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/auth";

export default function VerifyOTP({ phoneNumber, maskedPhone, onClose }) {
  const location = useLocation();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [error, setError] = useState("");
  const [otpArray, setOtpArray] = useState(["", "", "", "", "", ""]);
  const inputRefs = useRef([]);
  const OTP_DURATION_SECONDS = 30 * 60;

  const [otpTimer, setOtpTimer] = useState(30 * 60);
  const [resendCooldown, setResendCooldown] = useState(30); // 30 sec

  useEffect(() => {
    if (!phoneNumber) {
      navigate("/forgot-password");
    }
  }, [phoneNumber, navigate]);

  //  resend timer countdown
  useEffect(() => {
    if (otpTimer <= 0) return;

    const interval = setInterval(() => {
      setOtpTimer((prev) => prev - 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [otpTimer]);

  useEffect(() => {
    if (resendCooldown <= 0) return;

    const interval = setInterval(() => {
      setResendCooldown((prev) => prev - 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [resendCooldown]);

  const formatTime = (seconds) => {
    const mins = String(Math.floor(seconds / 60)).padStart(2, "0");
    const secs = String(seconds % 60).padStart(2, "0");
    return `${mins}:${secs}`;
  };

  // ---------------- VERIFY OTP ---------------- //
  const handleChange = (index, value) => {
    const digit = value.replace(/\D/g, "").slice(0, 1);

    const newOtp = [...otpArray];
    newOtp[index] = digit;
    setOtpArray(newOtp);
    setError("");

    if (digit && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index, e) => {
    if (e.key === "Backspace") {
      const newOtp = [...otpArray];

      if (newOtp[index]) {
        newOtp[index] = "";
        setOtpArray(newOtp);
      } else if (index > 0) {
        inputRefs.current[index - 1]?.focus();
      }
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);

    const newOtp = ["", "", "", "", "", ""];
    for (let i = 0; i < pasted.length; i++) {
      newOtp[i] = pasted[i];
    }

    setOtpArray(newOtp);
    const focusIndex = Math.min(pasted.length, 5);
    inputRefs.current[focusIndex]?.focus();
  };

  const handleVerifyOTP = async (e) => {
    e.preventDefault();

    const finalOtp = otpArray.join("");

    if (!/^\d{4,10}$/.test(finalOtp)) {
      setError("Enter a valid 6-digit OTP");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await fetch(`${API_BASE}/otp/verify/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ phoneNumber, otp: finalOtp }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || data.message || "Invalid OTP");
      }

      onClose();
      navigate("/reset-password", { state: { phoneNumber } });
    } catch (err) {
      setError(err.message || "Verification failed");
    } finally {
      setLoading(false);
    }
  };

  const handleResendOTP = async () => {
    setError("");
    setResendLoading(true);

    try {
      const res = await fetch(`${API_BASE}/otp/resend/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ phoneNumber }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || data.message || "Failed to resend OTP");
      }

      setResendCooldown(30);
      setOtpTimer(30 * 60);

    } catch (err) {
      setError(err.message || "Failed to resend OTP");
    } finally {
      setResendLoading(false);
    }
  };

  return (
    <div className="otp-modal-overlay">
      <div className="otp-modal">
        <button type="button" className="otp-modal-close" onClick={onClose}>
          ×
        </button>
        <h2>Verify OTP</h2>

        <p>
          Enter the code sent to <b>{maskedPhone || phoneNumber}</b>
        </p>

          <form onSubmit={handleVerifyOTP}>
            <div className="otp-box-container" onPaste={handlePaste}>
              {otpArray.map((digit, index) => (
                <input key={index} ref={(el) => (inputRefs.current[index] = el)} type="text" id={`otp-${index}`} name={`otp-${index}`} inputMode="numeric" autoComplete={index === 0 ? "one-time-code" : "off"} maxLength={1} value={digit}
                onChange={(e) => handleChange(index, e.target.value)}
                onKeyDown={(e) => handleKeyDown(index, e)}
                className="otp-box"
                required />
              ))}
            </div>

            {error && <p className="error-text">{error}</p>}

            <button
              type="submit"
              disabled={loading || otpArray.join("").length < 4}
              className="otp-submit-btn"
              style={{ opacity: loading ? 0.6 : 1 }}
            >
              {loading ? "Verifying..." : "Verify OTP"}
            </button>
          </form>

          <p className="resend-otp" style={{ marginTop: "14px" }}>
            Didn’t receive OTP?{" "}
            {resendCooldown > 0 ? (
              <span className="resend-disabled" style={{ marginLeft: "9px" }}>
                Resend in {formatTime(resendCooldown)}
              </span>
            ) : (
              <span onClick={handleResendOTP} style={{ cursor: "pointer", marginLeft: "9px" }}>
                {resendLoading ? "Resending..." : "Resend"}
              </span>
            )}
          </p>
          {/* {otpTimer > 0 && (
            <p className="otp-timer-text">
              OTP expires in {formatTime(otpTimer)}
            </p>
          )} */}
        </div>
      </div>
  );
}