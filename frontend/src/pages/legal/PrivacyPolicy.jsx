import React, { useEffect } from "react";
import { updateMeta, updateOG } from "../../utils/updateOG";
import Header from "../../components/header/Header";
import Footer from "../../components/footer/Footer";

export default function PrivacyPolicy() {
  const today = new Date().toLocaleDateString("en-IN", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  useEffect(() => {
    updateMeta({
      title: "Privacy Policy | Vastrika Online Fashion Store",
      description:
        "Learn how Vastrika collects, uses, and protects your personal information when shopping on our platform.",
    });

    updateOG({
      title: "Privacy Policy | Vastrika Online Fashion Store",
      description:
        "Learn how Vastrika collects, uses, and protects your personal information when shopping on our platform.",
      image: window.location.origin + "/assets/image/logo/vastrika-logo.png",
      url: window.location.origin + "/privacy-policy",
    });
  }, []);

  return (
    <>
      <Header />

      <main className="app-layout">
        <div className="main-content">
          <section className="policy-wrapper">
            <div className="policy-container">

              {/* Heading */}
              <header className="privacy-heading">
                <h1>Privacy Policy</h1>
                <p className="privacy-date">
                  <strong>Effective Date:</strong> 12 February 2026 <br />
                  <strong>Last Updated:</strong> {today}
                </p>

                <p>
                  At <strong>Vastrika</strong>, we are committed to protecting your
                  personal information and your right to privacy. This Privacy
                  Policy explains how we collect, use, disclose, and safeguard your
                  information when you visit or make a purchase from our website.
                </p>
              </header>

              {/* Information */}
              <section className="privacy-information">
                <h3>1. Information We Collect</h3>
                <p>We may collect the following types of information:</p>

                <h4>Personal Information</h4>
                <ul>
                  <li>Full Name</li>
                  <li>Email Address</li>
                  <li>Phone Number</li>
                  <li>Shipping and Billing Address</li>
                </ul>

                <h4>Technical Information</h4>
                <ul>
                  <li>IP Address</li>
                  <li>Browser Type & Device Information</li>
                  <li>Cookies and Usage Data</li>
                </ul>

                <h4>Order Information</h4>
                <ul>
                  <li>Products Purchased</li>
                  <li>Transaction Details</li>
                  <li>Order History</li>
                </ul>
              </section>

              {/* Usage */}
              <section className="privacy-weuse">
                <h3>2. How We Use Your Information</h3>
                <ul>
                  <li>To process and deliver your orders</li>
                  <li>To provide customer support</li>
                  <li>To send order updates and notifications</li>
                  <li>To improve website performance and experience</li>
                  <li>To send promotional offers (with your consent)</li>
                  <li>To prevent fraud and ensure security</li>
                </ul>
              </section>

              {/* Sharing */}
              <section className="privacy-share">
                <h3>3. Sharing of Information</h3>
                <p>
                  We do not sell or trade your personal information. We may share
                  data with:
                </p>
                <ul>
                  <li>Payment gateway providers</li>
                  <li>Logistics and delivery partners</li>
                  <li>IT and analytics service providers</li>
                  <li>Legal authorities when required</li>
                </ul>
              </section>

              {/* Cookies */}
              <section className="privacy-tracking">
                <h3>4. Cookies & Tracking</h3>
                <p>We use cookies to:</p>
                <ul>
                  <li>Enhance your browsing experience</li>
                  <li>Remember login preferences</li>
                  <li>Analyze website traffic</li>
                  <li>Provide personalized recommendations</li>
                </ul>
              </section>

              {/* Security */}
              <section className="privacy-security">
                <h3>5. Data Security</h3>
                <ul>
                  <li>SSL encryption</li>
                  <li>Secure payment gateways</li>
                  <li>Restricted data access</li>
                  <li>Regular monitoring</li>
                </ul>
                <p>
                  While we implement strong safeguards, no method of transmission
                  is completely secure.
                </p>
              </section>

              {/* Rights */}
              <section className="privacy-rights">
                <h3>6. Your Rights</h3>
                <ul>
                  <li>Access your personal data</li>
                  <li>Request corrections</li>
                  <li>Request account deletion</li>
                  <li>Opt-out of marketing</li>
                </ul>
                <p>
                  Contact us at{" "}
                  <a href="mailto:support@vastrika.com" style={{ color: '#c5396a' }}>
                    support@vastrika.com
                  </a>
                </p>
              </section>

              {/* Retention */}
              <section className="privacy-retention">
                <h3>7. Data Retention</h3>
                <p>
                  We retain your information only as long as necessary for legal,
                  operational, and business purposes.
                </p>
              </section>

              {/* Children */}
              <section className="privacy-children">
                <h3>8. Children's Privacy</h3>
                <p>
                  Our services are not intended for individuals under 18 years of
                  age.
                </p>
              </section>

              {/* Changes */}
              <section className="privacy-change">
                <h3>9. Policy Updates</h3>
                <p>
                  We may update this Privacy Policy periodically. Changes will be
                  reflected on this page.
                </p>
              </section>

              {/* Contact */}
              <section className="privacy-contact">
                <h3>10. Contact Us</h3>
                <p>
                  Email:{" "}
                  <a href="mailto:support@vastrika.com">
                    support@vastrika.com
                  </a>
                  <br />
                  Phone: <a href="tel:+911234567890">+91 12345 67890</a>
                  <br />
                  Address: Contai, Purba Medinipur, West Bengal, India
                </p>
              </section>

            </div>
          </section>
        </div>
      </main>

      <Footer />
    </>
  );
}