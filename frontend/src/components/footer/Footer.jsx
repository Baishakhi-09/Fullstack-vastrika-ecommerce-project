import React, { useState } from "react";
import { Link } from "react-router-dom";

const API_BASE =
 import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/auth";

export default function Footer() {

    // newsletter
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("");
    const [messageType, setMessageType] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();

        const cleanEmail = email.trim().toLowerCase();

        if (!cleanEmail) {
            setMessage("Email address is required.");
            setMessageType("error");
            return;
        }

        setLoading(true);
        setMessage("");
        setMessageType("");

        try {
            const res = await fetch(`${API_BASE}/newsletter/subscribe/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email: cleanEmail }),
            });

            const data = await res.json();

            if (!res.ok) {
                setMessage(data.message || "Subscription failed.");
                setMessageType("error");
                return;
            }

            setMessage(data.message || "Subscribed successfully.");
            setMessageType("success");
            setEmail("");
        } catch (error) {
            setMessage("Something went wrong. Please try again.");
            setMessageType("error");
        } finally {
            setLoading(false);
        }
    };

    // dynamic year
    const currentYear = new Date().getFullYear();
    const [email, setEmail] = useState("");

    // const handleSubscribe = (e) => {
    //     e.preventDefault();

    //     if (!email) return;
        
    //     console.log("Subscribed:", email); // replace with API call
    //     setEmail("");
    // };

    return (
        <footer className="footer" role="contentinfo">
            <div className="footer-container">

                {/* About */}
                <div className="footer-column">
                    <h3>About Us</h3>
                    <p>
                        At Vastrika, we curate fashion that blends cultural elegance with modern design.
                        Every piece is selected to offer comfort, quality, and style for every occasion.
                    </p>

                    <h4>Follow Us</h4>
                    <a href="https://www.instagram.com" target="_blank" rel="noopener noreferrer" aria-label="Visit our Instagram">
                        <i className="fa fa-instagram"></i>
                    </a>
                </div>

                {/* Who We Are */}
                <div className="footer-column">
                    <h3>Who We Are</h3>
                    <ul>
                        <li><Link to="/about">About Us</Link></li>
                        <li><Link to="/contact">Contact Us</Link></li>
                    </ul>
                </div>

                {/* Help */}
                <div className="footer-column">
                    <h3>Help</h3>
                    <ul>
                        <li><Link to="/shipping-policy">Shipping & Delivery</Link></li>
                        <li><Link to="/cancellation-policy">Cancellation & Return</Link></li>
                        <li><Link to="/help-center">Help Center</Link></li>
                    </ul>
                </div>

                {/* Newsletter */}
                <div className="footer-column">
                    <h3>Newsletter</h3>
                    <p>Be the first to know about latest trends, offers and collections</p>

                    <form onSubmit={handleSubmit} noValidate>
                        <input type="email" name="email" id="newsletter-email" autoComplete="email" placeholder="Email Address" value={email} onChange={(e) => setEmail(e.target.value)} required aria-label="Email address" />
                        <button type="submit" disabled={loading}>{loading ? "Subscribing..." : "Subscribe"}</button>
                    </form>

                    {message && ( 
                        <p style={{ marginTop: "10px", fontSize: "14px", color: messageType === "success" ? "green" : "red", }}>
                            {message}
                        </p>
                    )}
                </div>
            </div>

            {/* Bottom */}
            <div className="footer-bottom">
                <p>
                    © {currentYear}{" "}
                    <span>
                        <Link to="/">Vastrika</Link>
                    </span>. All Rights Reserved.
                </p>

                <nav className="footer-links" aria-label="Footer links">
                    <Link to="/terms-and-conditions">Terms & Conditions</Link>
                    <Link to="/shipping-policy">Shipping Policy</Link>
                    <Link to="/cancellation-policy">Cancellation Policy</Link>
                    <Link to="/return-and-refund-policy">Return & Refund Policy</Link>
                    <Link to="/privacy-policy">Privacy Policy</Link>
                    <Link to="/sitemap">Site Map</Link>
                </nav>
            </div>
        </footer>
    );
}