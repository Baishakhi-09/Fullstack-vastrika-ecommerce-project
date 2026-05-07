import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import Header from "../../components/header/Header";
import Footer from "../../components/footer/Footer";

import orderIcon from "../../assets/image/icon/order-box.png";
import loginIcon from "../../assets/image/icon/login-icon.png";
import addressIcon from "../../assets/image/icon/address.png";
import accountIcon from "../../assets/image/icon/business-account.png";
import paymentIcon from "../../assets/image/icon/payment.png";
import contactIcon from "../../assets/image/icon/contact.png";

import { updateMeta, updateOG } from "../../utils/updateOG";
import { useAuth } from "../../context/AuthContext";

const Index = () => {
  const navigate = useNavigate();
  const { isLoggedIn } = useAuth();

  const handleProtectedRoute = (path) => {
    if (isLoggedIn) {
      navigate(path);
    } else {
      navigate("/login");
    }
  };

  // ---------- SEO ---------- //
  useEffect(() => {
    updateMeta({
      title: "My Account | Vastrika",
      description:
        "Manage your orders, profile, addresses, and payments securely on Vastrika.",
      keywords:
        "Vastrika account, manage orders, edit profile, address book ecommerce",
    });

    updateOG({
      title: "My Account | Vastrika",
      description:
        "Manage your orders, profile, addresses, and payments securely on Vastrika.",
      image: "/assets/image/logo/vastrika-logo.png",
      url: window.location.href,
    });
  }, []);

  return (
    <div className="page-wrapper account-page">
      <Header />

      <main className="main-content" role="main">
        <div className="account-container">
          <h1>Your Account</h1>

          <div className="account-grid">

            {/* Orders */}
            <button
              className="account-card"
              onClick={() => handleProtectedRoute("/orders")}
            >
              <img src={orderIcon} alt="Orders" />
              <div>
                <h3>Orders</h3>
                <p>Track, return or buy things again</p>
              </div>
            </button>

            {/* Profile */}
            <button
              className="account-card"
              onClick={() => handleProtectedRoute("/profile")}
            >
              <img src={loginIcon} alt="Profile" />
              <div>
                <h3>Profile</h3>
                <p>Edit login, name and mobile number</p>
              </div>
            </button>

            {/* Address */}
            <button
              className="account-card"
              onClick={() => handleProtectedRoute("/account/address")}
            >
              <img src={addressIcon} alt="Addresses" />
              <div>
                <h3>Addresses</h3>
                <p>Edit addresses for orders</p>
              </div>
            </button>

            {/* Business Account */}
            <button
              className="account-card"
              onClick={() => navigate("/seller")}
            >
              <img src={accountIcon} alt="Business Account" style={{ width: '70px' }} />
              <div>
                <h3>Your Business Account</h3>
              </div>
            </button>

            {/* Payment */}
            <button
              className="account-card"
              onClick={() => handleProtectedRoute("/payments")}
            >
              <img src={paymentIcon} alt="Payment" />
              <div>
                <h3>Payment</h3>
                <p>Edit or add payment methods</p>
              </div>
            </button>

            {/* Contact */}
            <button
              className="account-card"
              onClick={() => navigate("/contact")}
            >
              <img src={contactIcon} alt="Contact Us" />
              <div>
                <h3>Contact Us</h3>
                <p>Customer service via phone or chat</p>
              </div>
            </button>

          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default Index;