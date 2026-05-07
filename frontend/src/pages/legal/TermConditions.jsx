import React, { useEffect } from 'react'
import { updateMeta, updateOG } from '../../utils/updateOG';
import Header from '../../components/header/Header';
import Footer from '../../components/footer/Footer';

export default function TermsConditions() {

    const today = new Date().toLocaleDateString("en-IN", {
        day: "numeric",
        month: "long",
        year: "numeric",
    });

    useEffect(() => {
        updateMeta({
            title: "Terms & Conditions | Vastrika Online Shopping Policies",
            description:
                "Read Vastrika’s Terms & Conditions covering user accounts, orders, payments, returns, shipping, and website usage policies for secure online shopping.",
        });

        updateOG({
            title: "Terms & Conditions | Vastrika Online Shopping Policies",
            description:
                "Read Vastrika’s Terms & Conditions covering user accounts, orders, payments, returns, shipping, and website usage policies for secure online shopping.",
            image: window.location.origin + "/assets/image/logo/vastrika-logo.png",
            url: window.location.origin + "/",
        });
    }, []);

    return (
        <>
            <Header />

            <div className='app-layout'>
                <div className='main-content'>
                    <div className='term-wrapper'>
                        <div className='term-container'>

                            <div className='term-heading'>
                                <h1>Terms & Conditions</h1>
                                <p className='term-date'>
                                    Effective Date: 12 February 2026 <br />
                                    Last Updated: {today}
                                </p>

                                <p className='term-overview'>
                                    Welcome to <b>Vastrika</b>. These Terms & Conditions govern your access to and use of our website,
                                    services, and products available at <a href="/">www.vastrika.com</a>.
                                    <br /><br />
                                    By accessing, browsing, or purchasing from our website, you agree to be legally bound by these Terms.
                                    If you do not agree, please discontinue use of the website.
                                </p>
                            </div>

                            <div className='term-about'>
                                <h3>About Us</h3>
                                <p>
                                    Vastrika is an online fashion and lifestyle e-commerce platform offering curated clothing,
                                    accessories, and related products inspired by cultural elegance and modern design.
                                </p>
                            </div>

                            <div className='term-eligibility'>
                                <h3>Eligibility</h3>
                                <ul>
                                    <li>You must be at least 18 years old or use the website under parental/guardian supervision.</li>
                                    <li>You must be legally capable of entering into a binding contract under Indian law.</li>
                                    <li>You agree to provide accurate and complete information.</li>
                                </ul>
                            </div>

                            <div className='term-account'>
                                <h3>User Account & Registration</h3>
                                <ul>
                                    <li>You are responsible for maintaining the confidentiality of your account credentials.</li>
                                    <li>You agree to provide accurate and updated information.</li>
                                    <li>You are responsible for all activities under your account.</li>
                                </ul>
                                <p>
                                    Vastrika reserves the right to suspend or terminate accounts in case of suspicious or fraudulent activity.
                                </p>
                            </div>

                            <div className='term-product'>
                                <h3>Product Information & Pricing</h3>
                                <ul>
                                    <li>All products are subject to availability.</li>
                                    <li>We strive for accuracy but minor variations in color or design may occur.</li>
                                    <li>Prices are listed in INR (₹) and may change without prior notice.</li>
                                </ul>
                                <p>
                                    In case of pricing errors, we reserve the right to cancel orders and issue refunds.
                                </p>
                            </div>

                            <div className='term-order'>
                                <h3>Orders & Payments</h3>
                                <ul>
                                    <li>Orders are confirmed only after successful payment authorization.</li>
                                    <li>Payments are processed through secure third-party gateways.</li>
                                    <li>We do not store your payment details.</li>
                                </ul>

                                <p>Orders may be cancelled due to:</p>
                                <ul>
                                    <li>Fraud suspicion</li>
                                    <li>Stock unavailability</li>
                                    <li>Payment issues</li>
                                    <li>Incorrect pricing</li>
                                </ul>
                            </div>

                            <div className='term-shipping'>
                                <h3>Shipping & Delivery</h3>
                                <ul>
                                    <li>Delivery timelines are estimates and may vary.</li>
                                    <li>Shipping details are available in our Shipping Policy.</li>
                                    <li>Ownership transfers upon successful delivery.</li>
                                </ul>
                            </div>

                            <div className='term-returns'>
                                <h3>Returns, Refunds & Cancellation</h3>
                                <ul>
                                    <li>Items must be unused and in original condition.</li>
                                    <li>Returns must be initiated within the allowed timeframe.</li>
                                    <li>Refunds are processed after quality checks.</li>
                                </ul>
                                <p>
                                    Refer to our Return & Refund Policy for complete details.
                                </p>
                            </div>

                            <div className='term-property'>
                                <h3>Intellectual Property</h3>
                                <p>
                                    All content including logo, branding, designs, images, and website structure are the property of Vastrika.
                                    Unauthorized use, reproduction, or distribution is strictly prohibited.
                                </p>
                            </div>

                            <div className='term-activity'>
                                <h3>Prohibited Activities</h3>
                                <ul>
                                    <li>Fraudulent or illegal activities</li>
                                    <li>Hacking or attempting to disrupt the website</li>
                                    <li>Uploading harmful or malicious content</li>
                                    <li>Providing false information</li>
                                </ul>
                            </div>

                            <div className='term-limit'>
                                <h3>Limitation of Liability</h3>
                                <p>
                                    Vastrika shall not be liable for indirect or consequential damages, loss of profits,
                                    or service interruptions beyond our control.
                                </p>
                            </div>

                            <div className='term-force'>
                                <h3>Force Majeure</h3>
                                <p>
                                    We are not responsible for delays caused by events beyond our control such as natural disasters,
                                    government restrictions, or technical failures.
                                </p>
                            </div>

                            <div className='term-governinglaw'>
                                <h3>Governing Law</h3>
                                <p>
                                    These Terms shall be governed by the laws of India. Any disputes shall be subject to
                                    the jurisdiction of courts in West Bengal, India.
                                </p>
                            </div>

                            <div className='term-contact'>
                                <h3>Contact Information</h3>
                                <p>
                                    For any queries regarding these Terms:
                                    <br />
                                    <b>Vastrika – Your Style, Your Culture</b>
                                    <br />
                                    Email: <a href="mailto:support@vastrika.com">support@vastrika.com</a>
                                    <br />
                                    Phone: <a href="tel:+91XXXXXXXXXX">+91 XXXXXXXXXX</a>
                                    <br />
                                    Address: Contai, Purba Medinipur, West Bengal, India
                                </p>
                            </div>

                        </div>
                    </div>
                </div>
            </div>

            <Footer />
        </>
    )
}