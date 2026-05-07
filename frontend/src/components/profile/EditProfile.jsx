import { useState, useEffect } from "react";
import { getCountries, getStatesOfCountry } from "@countrystatecity/countries-browser";
import { useAuth } from "../../context/AuthContext";
import { toast } from "react-toastify";

const EditProfile = ({ onCancel }) => {
    const { user, updateProfile, fetchUser } = useAuth();

    const [formData, setFormData] = useState({
        first_name: "",
        phone: "",
        alternate_phone: "",
        gender: "",
        address_line_1: "",
        address_line_2: "",
        city: "",
        state: "",
        pincode: "",
        country: "India",
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");
    const [countries, setCountries] = useState([]);
    const [states, setStates] = useState([]);
    const [phoneDialCode, setPhoneDialCode] = useState("91");
    const [alternateDialCode, setAlternateDialCode] = useState("91");

    const removeDialCode = (phone = "") => {
        const value = String(phone || "").trim();

        if (!value.startsWith("+")) {
            return value;
        }

        const onlyDigits = value.replace(/\D/g, "");
        if (!onlyDigits) return "";

        const knownCodes = countries
            .map((c) => String(c.phonecode || ""))
            .filter(Boolean)
            .sort((a, b) => b.length - a.length);

        const matchedCode = knownCodes.find((code) => onlyDigits.startsWith(code));
        if (!matchedCode) return onlyDigits;

        return onlyDigits.slice(matchedCode.length);
    };

    // Prefill user data
    useEffect(() => {
        if (!user || !countries.length) return;

        const fallbackCountry = user.country || "India";
        const selectedCountry = countries.find((c) => c.name === fallbackCountry);
        const fallbackDialCode = selectedCountry?.phonecode || "91";

        setFormData({
            first_name: user.first_name || "",
            phone: removeDialCode(user.phone || ""),
            alternate_phone: removeDialCode(user.alternate_phone || ""),
            gender: user.gender || "",
            address_line_1: user.address_line_1 || "",
            address_line_2: user.address_line_2 || "",
            city: user.city || "",
            state: user.state || "",
            pincode: user.pincode || "",
            country: fallbackCountry,
        });

        setPhoneDialCode(fallbackDialCode);
        setAlternateDialCode(fallbackDialCode);
    }, [user, countries]);

    // Load Countries
    useEffect(() => {
        const loadCountries = async () => {
            try {
                const countryList = await getCountries();
                setCountries(Array.isArray(countryList) ? countryList : []);
            } catch (error) {
                console.error("Failed to load countries:", error);
                setCountries([]);
            }
        };
        
        loadCountries();
    }, []);

    // Load states + phone code based on selected country
    useEffect(() => {
        const loadStates = async () => {
            if (!countries.length || !formData.country) {
                setStates([]);
                return;
            }
            
            try {
                const selectedCountry = countries.find(
                    (country) => country.name === formData.country
                );

                if (!selectedCountry) {
                    setStates([]);
                    return;
                }

                setPhoneDialCode(selectedCountry.phonecode || "91");
                setAlternateDialCode(selectedCountry.phonecode || "91");
                
                if (!selectedCountry?.iso2) {
                    setStates([]);
                    return;
                }
                
                const stateList = await getStatesOfCountry(selectedCountry.iso2);
                setStates(Array.isArray(stateList) ? stateList : []);
            } catch (error) {
                console.error("Failed to load states:", error);
                setStates([]);
            }
        };
        
        loadStates();
    }, [formData.country, countries, user]);

    // Handle input change
    const handleChange = (e) => {
        const { name, value } = e.target;

        setFormData(prev => ({
            ...prev,
            [name]: value,
            ...(name === "country" ? { state: "" } : {}),
        }));
    };

    const handlePhoneDialCodeChange = (e) => {
        setPhoneDialCode(e.target.value);
    };

    const handleAlternateDialCodeChange = (e) => {
        setAlternateDialCode(e.target.value);
    };


    // Validation
    const validateForm = () => {
        if (!formData.first_name.trim()) {
            return "Full name is required";
        }
        if (formData.phone && !/^[0-9]{10}$/.test(formData.phone.trim())) {
            return "Enter valid 10-digit phone number";
        }
        if (!formData.address_line_1.trim()) {
            return "Address is required";
        }
        if (!formData.city.trim()) {
            return "City is required";
        }
        if (!formData.state.trim()) {
            return "State is required";
        }
        if (!formData.pincode.trim()) {
            return "Pincode is required";
        }

        return null;
    };

    // Submit handler
    const handleSubmit = async (e) => {
        e.preventDefault();

        const validationError = validateForm();
        if (validationError) {
            toast.error(validationError);
            return;
        }

        setLoading(true);
        setError("");
        setMessage("");

        try {
            const payload = {
                ...formData,
                phone: formData.phone ? `+${phoneDialCode}${formData.phone}` : "",
                alternate_phone: formData.alternate_phone
                    ? `+${alternateDialCode}${formData.alternate_phone}`
                    : "",
            };

            const result = await updateProfile(payload);

            if (result.success) {
                await fetchUser(false);
                toast.success(result.message || "Profile updated successfully.");
                setTimeout(() => onCancel(), 700);
            } else {
                toast.error(result.message || "Update failed.");
            }
        } catch (err) {
            console.error(err);
            toast.error("Something went wrong.");
        } finally {
            setLoading(false);
        }
    };

    const phoneCodeCountries = countries.filter((country) => country.phonecode);

    return (
        <>
            <div className="modal-body">
                <form id="editProfileForm" onSubmit={handleSubmit}>
                    <input type="text" name="first_name" value={formData.first_name} onChange={handleChange} placeholder="Full Name" autoComplete="name" required />
                    <div className="phone-field">
                        <select name="phone_dial_code" id="phone_dial_code" className="phone-code-select"  value={phoneDialCode} onChange={handlePhoneDialCodeChange} aria-label="Select phone country code">
                            {phoneCodeCountries
                            .map((country, index) => (
                                <option key={`${country.iso2}-${index}`} value={country.phonecode || ""}>
                                    {country.name} (+{country.phonecode || ""})
                                </option>
                            ))}
                        </select>
                        <input type="tel" name="phone" value={formData.phone} onChange={handleChange} placeholder="Phone Number" autoComplete="tel-national" required />
                    </div>
                    <div className="phone-field" style={{ height: "48px" }}>
                        <select name="alternate_dial_code" id="alternate_dial_code" className="phone-code-select" value={alternateDialCode} onChange={handleAlternateDialCodeChange} aria-label="Select alternate phone country code">
                            {phoneCodeCountries
                            .map((country, index) => (
                                <option key={`${country.iso2}-${index}`} value={country.phonecode || ""}>
                                    {country.name} (+{country.phonecode || ""})
                                </option>
                            ))}
                        </select>
                        <input type="tel" name="alternate_phone" value={formData.alternate_phone} onChange={handleChange} placeholder="Alternate Phone Number" autoComplete="tel-national" />
                    </div>
                    <div className="form-group">
                        <legend className="form-label" style={{ fontSize: "14px" }}>Gender</legend>

                        <div className="radio-group">
                            <label className="radio-option" htmlFor="male">
                                <input type="radio" id="male" name="gender" value="male" checked={formData.gender === "male"} onChange={handleChange} />
                                Male
                            </label>
                            <label className="radio-option" htmlFor="female">
                                <input type="radio" id="female" name="gender" value="female" checked={formData.gender === "female"} onChange={handleChange} />
                                Female
                            </label>
                            <label className="radio-option" htmlFor="other">
                                <input type="radio" id="other" name="gender" value="other" checked={formData.gender === "other"} onChange={handleChange} />
                                Other
                            </label>
                        </div>
                    </div>
                    <textarea style={{ height: "35px" }} name="address_line_1" onChange={handleChange} placeholder="Address" autoComplete="address-line1" value={formData.address_line_1} required />
                    <textarea style={{ height: "35px" }} name="address_line_2" onChange={handleChange} placeholder="Address (Alternative)" autoComplete="address-line2" value={formData.address_line_2} />
                    <input type="text" name="city" placeholder="City" autoComplete="address-level2" value={formData.city} onChange={handleChange} required />
                    <select name="country" id="country" value={formData.country} autoComplete="country-name" onChange={handleChange} required>
                        <option value="">Select Country</option>
                        {countries.map((country) => (
                            <option key={country.iso2} value={country.name}>
                                {country.name}
                            </option>
                        ))}
                    </select>
                    <input type="text" name="pincode" placeholder="Pincode" autoComplete="postal-code" value={formData.pincode} onChange={handleChange} required />
                    <select name="state" value={formData.state} onChange={handleChange} required disabled={!formData.country}>
                        <option value="">
                            {formData.country ? "Select State" : "Select Country First"}
                        </option>
                        {states.map((state) => (
                            <option key={state.iso2 || state.name} value={state.name}>
                                {state.name}
                            </option>
                        ))}
                    </select>                

                    {message && <p>{message}</p>}
                </form>
            </div>
            <div className="modal-footer">
                <button type="button" className="profile--cancel-btn" onClick={onCancel} disabled={loading}>Cancel</button>

                <button type="submit" form="editProfileForm" className="profile--save-btn" disabled={loading}>
                    {loading ? "Saving..." : "Save Details"}
                </button>
            </div>
        </>
    );
};

export default EditProfile;