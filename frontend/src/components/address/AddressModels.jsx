import { useEffect, useState } from "react";

const AddressModels = ({ isOpen, onClose, onSave }) => {
    const [formData, setFormData] = useState({
        fullName: "",
        mobile: "",
        pincode: "",
        state: "",
        houseNumber: "",
        address: "",
        locality: "",
        city: "",
        addressType: "home",
    });

    // Close on ESC key
    useEffect(() => {
        const handleESC = (e) => {
            if (e.key === "Escape") onClose();
        };
        window.addEventListener("keydown", handleESC);
        return () => window.removeEventListener("keydown", handleESC);
    }, [onClose]);

    // Prevent background scroll
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = "hidden";
        } else {
            document.body.style.overflow = "auto";
        }
    }, [isOpen]);

    if (!isOpen) return null;

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();

        // Safe call
        if (onSave) {
            onSave(formData);
        }

        onClose();
    };

    return (
        <div className="modal-overlay--address__profile" onClick={onClose} aria-modal="true" role="dialog" aria-labelledby="addressModalTitle">
            <div className="modal-container--address__profile" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header--address__profile">
                    <h3 id="addressModalTitle">Add New Address</h3>
                </div>

                <form className="modal-body--address__profile" onSubmit={handleSubmit}>
                    <input type="text" name="fullName" placeholder="Full name *" value={formData.fullName} onChange={handleChange} required />
                    <input type="tel" name="mobile" placeholder="Mobile Number *" value={formData.mobile} onChange={handleChange} required />

                    <div className="row--address__profile">
                        <input type="text" name="pincode" placeholder="Pincode *" value={formData.pincode} onChange={handleChange} required />
                        <input type="text" name="state" placeholder="State *" value={formData.state} onChange={handleChange} required />
                    </div>

                    <input type="text" name="houseNumber" placeholder="House Number *" value={formData.houseNumber} onChange={handleChange} required />
                    <textarea name="address" placeholder="Address (Building, Street, Area) *" value={formData.address} onChange={handleChange} required />

                    <input type="text" name="locality" placeholder="Locality/ Town *" value={formData.locality} onChange={handleChange} required />
                    <input type="text" name="city" placeholder="City/ District" value={formData.city} onChange={handleChange} />

                    <div className="text">Type of Address *</div>
                    <div className="row--address__profile">
                        <label>
                            <input type="radio" name="addressType" value="home" checked={formData.addressType === "home"} onChange={handleChange} />
                            <span>Home</span>
                        </label>

                        <label>
                            <input type="radio" name="addressType" value="office" checked={formData.addressType === "office"} onChange={handleChange} />
                            <span>Office</span>
                        </label>
                    </div>

                    <div className="modal-footer--address__profile">
                        <button type="button" className="cancel-btn" onClick={onClose}>Cancel</button>
                        <button type="submit" className="save-btn">Save</button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AddressModels;