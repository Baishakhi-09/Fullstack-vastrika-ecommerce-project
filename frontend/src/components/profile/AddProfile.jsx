import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";

const AddProfile = () => {
    const { user, updateProfile } = useAuth();

    const [formData, setFormData] = useState({
        fullName: "",
        phone: "",
        address: "",
    });

    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("");

    // Prefill user data
    useEffect(() => {
        if (user) {
            setFormData({
                fullName: user.first_name || "",
                phone: user.phone || "",
                address: user.address || "",
            });
        }
    }, [user]);

    // Handle change
    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    // Validation
    const validate = () => {
        if (!formData.fullName.trim()) return "Full name is required";
        if (!/^[0-9]{10}$/.test(formData.phone))
            return "Enter valid 10-digit phone number";
        if (!formData.address.trim()) return "Address is required";
        return null;
    };

    // Submit handler
    const handleSubmit = async (e) => {
        e.preventDefault();

        const error = validate();
        if (error) {
            setMessage(error);
            return;
        }

        try {
            setLoading(true);
            setMessage("");

            await updateProfile(formData);

            setMessage("Profile updated successfully");
        } catch (err) {
            console.error(err);
            setMessage("Failed to update profile. Try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <section className="add-profile" aria-label="User profile form">
            <h2>Your Profile</h2>

            <form onSubmit={handleSubmit} noValidate>

                {/* Full Name */}
                <div className="form-group">
                    <label htmlFor="fullName">Full Name</label>
                    <input id="fullName" name="fullName" type="text" value={formData.fullName} onChange={handleChange} placeholder="Enter your full name" required />
                </div>

                {/* Phone */}
                <div className="form-group">
                    <label htmlFor="phone">Mobile Number</label>
                    <input id="phone" name="phone" type="tel" value={formData.phone} onChange={handleChange} placeholder="Enter 10-digit phone number" maxLength="10" required />
                </div>

                {/* Address */}
                <div className="form-group">
                    <label htmlFor="address">Address</label>
                    <textarea id="address" name="address" value={formData.address} onChange={handleChange} placeholder="Enter your address" rows="3" required />
                </div>

                {/* Message */}
                {message && (
                    <p className={`form-message ${
                            message.includes("success") ? "success" : "error"
                        }`}>
                        {message}
                    </p>
                )}

                {/* Submit */}
                <button type="submit" className="add__profile--save-btn" disabled={loading}>
                    {loading ? "Saving..." : "Save Profile"}
                </button>

            </form>
        </section>
    );
};

export default AddProfile;