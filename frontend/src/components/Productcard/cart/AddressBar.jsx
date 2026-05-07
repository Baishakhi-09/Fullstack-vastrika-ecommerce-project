import { useCart } from "../../../context/CartContext";

const AddressBar = ({ openAddressModal }) => {
    const { address } = useCart();

    // Safe fallback
    const formattedAddress = address?.pincode
        ? `${address.pincode}, ${address.city || ""}, ${address.state || ""}`
        : null;

    return (
        <div className="address--cart" role="region" aria-label="Delivery address">

            <div className="address-info">
                <strong>Deliver to:</strong>{" "}
                {formattedAddress || "Enter your delivery location"}
            </div>

            <button type="button" className="change-btn--cart" onClick={openAddressModal} aria-label="Change delivery location">
                {formattedAddress ? "Change" : "Enter PIN CODE"}
            </button>

        </div>
    );
};

export default AddressBar;