import { useLocation } from "react-router-dom";
import { useEffect, useState, useMemo } from "react";

// import CheckoutHeader from "../checkout/CheckoutHeader";
import AddressBar from "./AddressBar";
import CartList from "./CartList";
import CartSummary from "./CartSummary";
import AddressModels from "../../address/AddressModels";
import Footer from "../../footer/Footer";

import { updateMeta, updateOG } from "../../../utils/updateOG";
import { useCart } from "../../../context/CartContext";

import shopCart from "../../../assets/image/cart-icon.png";

const stepMap = {
    "/cart": "BAG",
    "/address": "ADDRESS",
    "/payment": "PAYMENT",
};

const CartPage = () => {
    const location = useLocation();

    const { cart = [] } = useCart();

    const [showAddressModal, setShowAddressModal] = useState(false);
    const [address, setAddress] = useState({
        pincode: "",
        city: "",
        state: "",
    });

    // Step detection
    const step = stepMap[location.pathname] || "BAG";

    // Cart state
    const isCartPage = location.pathname === "/cart";

    const isCartEmpty = useMemo(
        () => isCartPage && cart.length === 0,
        [isCartPage, cart]
    );

    // SEO Meta
    useEffect(() => {
        updateMeta({
            title: "Shopping Bag | Vastrika",
            description:
                "Review items in your shopping bag at Vastrika before checkout",
            keywords:
                "Vastrika cart, shopping bag, checkout fashion India, ecommerce cart",
        });

        updateOG({
            title: "Shopping Bag | Vastrika",
            description:
                "Review items in your shopping bag at Vastrika before checkout",
            image: "/assets/image/logo/vastrika-logo.png",
            url: window.location.href,
        });
    }, []);

    // Save address
    const handleSaveAddress = (data) => {
        setAddress(data);
        setShowAddressModal(false);
    };

    return (
        <>
            {/* Header */}
            {/* <CheckoutHeader activeStep={step} /> */}

            <div className="app-layout">
                <main className="main-content">
                    <div className="cart-wrapper">
                        <div className="cart-container">
                            {/* <div className="cart-page"> */}

                                {/* EMPTY CART */}
                                {/* {isCartPage && isCartEmpty && ( */}
                                {isCartEmpty ? (
                                        <div className="empty-cart" role="region" aria-label="Empty cart">
                                            <img src={shopCart} alt="Empty shopping cart" />
                                            <h2>Your Shopping Cart is empty</h2>
                                            <p>
                                                Check your saved items or{" "}
                                                <a href="/">continue shopping</a>
                                            </p>
                                        </div>
                                    ) : (
                                    <>
                                        {/* LEFT SIDE */}
                                        <div className="cart-left">
                                            <AddressBar openAddressModal={() => setShowAddressModal(true)} />
                                            <CartList />
                                        </div>
                                    
                                        {/* RIGHT SIDE */}
                                        <div className="cart-right">
                                            <CartSummary />
                                        </div>
                                    </>
                                )}

                                {/* ADDRESS MODAL */}
                                {showAddressModal && !isCartEmpty && (
                                    <AddressModels onClose={() => setShowAddressModal(false)} onSave={handleSaveAddress} />
                            )}
                        </div>
                    </div>
                </main>
            </div>

            {/* Footer */}
            <Footer />
        </>
    );
};

export default CartPage;