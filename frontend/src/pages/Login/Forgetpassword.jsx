import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import logo from "../../assets/image/logo/vastrika-logo.png";
import { updateMeta, updateOG } from "../../utils/updateOG";
import { getCountries, getCountryCallingCode } from "libphonenumber-js";
import { toast } from "react-toastify";
import VerifyOTP from "./VerifyOTP";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/auth";

const countryCodes = getCountries().map((country) => ({
  iso: country,
  code: `+${getCountryCallingCode(country)}`,
}));

export default function Forgetpassword() {
  const navigate = useNavigate();

  const [selectedCountryCode, setSelectedCountryCode] = useState("IN");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showOtpModal, setShowOtpModal] = useState(false);
  const [otpPhoneNumber, setOtpPhoneNumber] = useState("");
  const [maskedPhone, setMaskedPhone] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    updateMeta({
      title: "Forgot Password | Reset Your Vastrika Account Securely",
      description:
        "Forgot your Vastrika account password? Reset it securely and regain access to your account in minutes.",
    });

    updateOG({
      title: "Forgot Password | Reset Your Vastrika Account Securely",
      description:
        "Forgot your Vastrika account password? Reset it securely and regain access to your account in minutes.",
      image: window.location.origin + "/assets/image/logo/vastrika-logo.png",
      url: window.location.origin + "/",
    });
  }, []);

  // -------------------- Validation -------------------- //
  const validatePhone = (phone) => /^\d{6,15}$/.test(phone);

  const handlePhoneChange = (e) => {
    const onlyDigits = e.target.value.replace(/\D/g, "").slice(0, 15);
    setPhoneNumber(onlyDigits);
    if (error) setError("");
    if (success) setSuccess("");
  };

  // -------------------- Send OTP -------------------- //
  const handleSendOTP = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess("");

    const trimmedPhone = phoneNumber.trim();
    const fullPhoneNumber = `+${getCountryCallingCode(selectedCountryCode)}${trimmedPhone}`;

    if (!validatePhone(trimmedPhone)) {
      setError("Please enter a valid mobile number.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/otp/send/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ phoneNumber: fullPhoneNumber }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.message || "Failed to send OTP");
      }

      setOtpPhoneNumber(data.phoneNumber || fullPhoneNumber);
      setMaskedPhone(data.maskedPhone || fullPhoneNumber);
      setShowOtpModal(true);
    } catch (err) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-layout">
      <div className="main-content">
        <div className="auth-wrapper--forget__password">
          <div className="auth-container--forget__password">
            <div className="row">
              <Link to="/">
                <img src={logo} alt="Vastrika Logo" />
              </Link>

              <h1>Forgot Password?</h1>

              <p className="information-text--forget__password">
                Enter your registered mobile number to receive an OTP.
              </p>

              {/* ---------------- Status Messages ---------------- */}
              {error && <p className="error-text">{error}</p>}
              {success && <p className="success-text">{success}</p>}

              {/* ---------------- Form ---------------- */}
              <form onSubmit={handleSendOTP} noValidate>
                <div className="phone-input-group">
                  <select id="countryCode" name="countryCode" value={selectedCountryCode} onChange={(e) => setSelectedCountryCode(e.target.value)} className="country-code-select">
                    {countryCodes.map((country) => (
                      <option key={country.iso} value={country.iso}>
                        {country.code}
                      </option>
                    ))}
                  </select>
                  <input type="tel" id="phone" name="phone" autoComplete="tel-national" inputMode="numeric" value={phoneNumber} placeholder="Enter mobile number" 
                  onChange={handlePhoneChange} maxLength={15} required />
                </div>

                <button type="submit" disabled={loading}>
                  {loading ? "Sending OTP..." : "Send OTP"}
                </button>
              </form>
            </div>
          </div>
        </div>
        {showOtpModal && (
          <VerifyOTP phoneNumber={otpPhoneNumber} maskedPhone={maskedPhone} onClose={() => setShowOtpModal(false)}/>
        )}
      </div>
    </div>
  );
}