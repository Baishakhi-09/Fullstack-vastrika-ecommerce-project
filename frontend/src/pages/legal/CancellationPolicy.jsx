import React, { useEffect } from "react";
import Header from "../../components/header/Header";
import Footer from "../../components/footer/Footer";
import { updateMeta, updateOG } from "../../utils/updateOG";

const CancellationPolicy = () => {

    useEffect(() => {
        updateMeta({
            title: "Cancellation Policy | Vastrika",
            description:
                "Learn about Vastrika’s order cancellation process, eligibility, refund timelines, and important conditions for prepaid and COD orders.",
        });

        updateOG({
            title: "Cancellation Policy | Vastrika",
            description:
                "Understand how order cancellations, refunds, and eligibility work at Vastrika.",
            image: window.location.origin + "/assets/image/logo/vastrika-logo.png",
            url: window.location.href,
        });
    }, []);

    return (
        <div className="page-wrapper cancel-page">
            <Header />

            <main className="main-content" role="main">
                <div className="cancel-wrapper">
                    <div className="cancel-container">

                        <header className="cancel-heading">
                            <h1>Cancellation Policy</h1>
                            <p>
                                At <strong>Vastrika</strong>, we strive to provide a seamless shopping experience. 
                                This Cancellation Policy outlines the terms and conditions under which you may cancel an order placed on our platform.
                            </p>
                        </header>

                        {/* Before Shipment */}
                        <section className="cancel-order">
                            <h2>1. Cancellation Before Shipment</h2>
                            <ul>
                                <li>
                                    Orders can be cancelled within <strong>24 hours of placement</strong> or before dispatch, whichever occurs earlier.
                                </li>
                                <li>
                                    To cancel, visit <strong>My Orders</strong> in your account or contact our support team.
                                </li>
                                <li>
                                    Once approved, refunds will be initiated to the original payment method.
                                </li>
                            </ul>
                        </section>

                        {/* After Shipment */}
                        <section className="cancel-shipment">
                            <h2>2. Cancellation After Shipment</h2>
                            <ul>
                                <li>Orders that have already been shipped cannot be cancelled directly.</li>
                                <li>You may refuse delivery at the time of arrival.</li>
                                <li>
                                    Alternatively, you may initiate a return after delivery as per our <strong>Return & Refund Policy</strong>.
                                </li>
                                <li>Shipping charges (if applicable) are non-refundable after dispatch.</li>
                            </ul>
                        </section>

                        {/* Prepaid */}
                        <section className="cancel-prepaid-orders">
                            <h2>3. Prepaid Order Cancellation</h2>
                            <ul>
                                <li>Refunds are processed within <strong>5–7 business days</strong> after approval.</li>
                                <li>The amount is credited to the original payment method.</li>
                                <li>Processing time may vary depending on your bank or payment provider.</li>
                            </ul>
                        </section>

                        {/* COD */}
                        <section className="cancel-cash-delivery">
                            <h2>4. Cash on Delivery (COD) Orders</h2>
                            <ul>
                                <li>COD orders can be cancelled before shipment.</li>
                                <li>
                                    Repeated cancellations may result in restrictions on future COD orders.
                                </li>
                            </ul>
                        </section>

                        {/* Company Cancellation */}
                        <section className="cancel-vas">
                            <h2>5. Cancellation by Vastrika</h2>
                            <p>We reserve the right to cancel orders under the following circumstances:</p>
                            <ul>
                                <li>Product unavailability</li>
                                <li>Pricing or product information errors</li>
                                <li>Payment verification issues</li>
                                <li>Suspected fraudulent activity</li>
                            </ul>
                            <p>
                                In such cases, customers will be notified and eligible refunds will be processed promptly.
                            </p>
                        </section>

                        {/* Non cancellable */}
                        <section className="cancel-item--policy">
                            <h2>6. Non-Cancellable Items</h2>
                            <ul>
                                <li>Customized or personalized products</li>
                                <li>Limited edition or clearance sale items</li>
                                <li>Products marked as <strong>“Non-Cancellable”</strong></li>
                            </ul>
                        </section>

                        {/* Contact */}
                        <section className="cancel-contact--policy">
                            <h2>7. Contact Information</h2>
                            <p>If you have any questions regarding cancellations, please contact us:</p>

                            <ul className="contact-list">
                                <li>
                                    Email:{" "}
                                    <a href="mailto:support@vastrika.com">
                                        support@vastrika.com
                                    </a>
                                </li>
                                <li>
                                    Phone:{" "}
                                    <a href="tel:+911234567890">
                                        +91 12345 67890
                                    </a>
                                </li>
                                <li>
                                    Support Hours: Monday – Saturday, 10:00 AM – 6:00 PM
                                </li>
                            </ul>
                        </section>

                    </div>
                </div>
            </main>

            <Footer />
        </div>
    );
};

export default CancellationPolicy;