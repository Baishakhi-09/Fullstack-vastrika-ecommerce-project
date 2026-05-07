import React, { useState } from "react";
import CheckoutHeader from "../components/Productcard/checkout/CheckoutHeader";
import { useCart } from "../context/CartContext";
import CartPage from "../components/Productcard/cart/CartPage";
import AddressBar from "../components/Productcard/cart/AddressBar";
import AddressModel from "../components/Productcard/cart/AddressModel";

const Cart = () => {
    // Get cart data from context (correct way)
    const { cart } = useCart();

    const [showAddressModal, setShowAddressModal] = useState(false);

    const [address, setAddress] = useState({
        pincode: "",
        city: "",
        state: "",
    });

    return (
        <div className="cart-page">
            {/* Step Header */}
            <CheckoutHeader step="BAG" />

            {/* Cart Items */}
            <CartPage cartItems={cart} />

            {/* Address Section */}
            <AddressBar
                address={address} 
                onChangeClick={() => setShowAddressModal(true)} 
            />

            {/* Address Modal (conditionally render) */}
            {showAddressModal && (
                <AddressModel
                    address={address}
                    setAddress={setAddress}
                    closeModal={() => setShowAddressModal(false)}
                />
            )}
        </div>
    );
};

export default Cart;