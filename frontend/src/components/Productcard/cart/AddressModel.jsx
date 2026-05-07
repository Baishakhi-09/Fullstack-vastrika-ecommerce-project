import { useEffect, useState } from "react";

const AddressModel = ({ isOpen, onClose, onSave }) => {
    const [address, setAddress] = useState({
        pincode: "",
        city: "",
        state: "",
    });

    // Close on ESC key
    useEffect(() => {
        const handleEsc = (e) => {
            if (e.key === "Escape") onClose();
        };

        if (isOpen) {
            window.addEventListener("keydown", handleEsc);
            document.body.style.overflow = "hidden";
        }

        return () => {
            window.removeEventListener("keydown", handleEsc);
            document.body.style.overflow = "auto";
        };
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    const handleChange = (e) => {
        const { name, value } = e.target;
        setAddress((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = () => {
        if (!address.pincode || !address.city || !address.state) {
            alert("Please fill all fields");
            return;
        }

        onSave(address);
        onClose();
    };

    return (
        <div className="modal-overlay" onClick={onClose} role="dialog" aria-modal="true" aria-labelledby="addressModalTitle">
            <div className="modal-box" onClick={(e) => e.stopPropagation()}>
                <h3 id="addressModalTitle">Enter Delivery Address</h3>

                <div className="address-form">
                    <input type="text" name="pincode" placeholder="Pincode" value={address.pincode} onChange={handleChange} required />
                    <input type="text" name="city" placeholder="City" value={address.city} onChange={handleChange} required />
                    <input type="text" name="state" placeholder="State" value={address.state} onChange={handleChange} required />
                </div>

                <div className="modal-actions">
                    <button type="button" className="btn-cancel" onClick={onClose}>Cancel</button>
                    <button type="button" className="btn-save" onClick={handleSubmit}>Save Address</button>
                </div>
            </div>
        </div>
    );
};

export default AddressModel;