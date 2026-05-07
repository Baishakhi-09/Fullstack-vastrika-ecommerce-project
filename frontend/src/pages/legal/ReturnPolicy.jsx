import React, { useEffect } from "react";
import Header from "../../components/header/Header";
import Footer from "../../components/footer/Footer";
import { updateMeta, updateOG } from "../../utils/updateOG";

export default function ReturnPolicy() {
  const today = new Date().toLocaleDateString("en-IN", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  useEffect(() => {
    updateMeta({
      title: "Return & Refund Policy | Vastrika",
      description:
        "Read Vastrika’s Return & Refund Policy for easy returns, exchanges, refund timelines, and secure online shopping experience.",
    });

    updateOG({
      title: "Return & Refund Policy | Vastrika",
      description:
        "Read Vastrika’s Return & Refund Policy for easy returns, exchanges, refund timelines, and secure online shopping experience.",
      image: window.location.origin + "/assets/image/logo/vastrika-logo.png",
      url: window.location.origin + "/return-policy",
    });
  }, []);

  return (
    <>
      <Header />

      <main className="app-layout">
        <div className="main-content">
          <section className="refund-wrapper">
            <div className="refund-container">

              {/* Heading */}
              <header className="refund-heading">
                <h1>Return & Refund Policy</h1>
                <p className="policy-date">
                  <strong>Last Updated:</strong> {today}
                </p>
                <p>
                  At <strong>Vastrika</strong>, customer satisfaction is our
                  priority. If you are not completely satisfied with your
                  purchase, we are here to help. Please review our policy below
                  for return eligibility, process, and timelines.
                </p>
              </header>

              {/* Eligibility */}
              <section className="refund-eligibile">
                <h3>1. Return Eligibility</h3>
                <p>You may request a return if:</p>
                <ul>
                  <li>The product is unused, unworn, and unwashed</li>
                  <li>All original tags and packaging are intact</li>
                  <li>The request is made within <strong>7 days of delivery</strong></li>
                  <li>The item is not listed under non-returnable products</li>
                </ul>
                <p>
                  Items showing signs of use, damage, or alteration will not be
                  accepted.
                </p>
              </section>

              {/* Non-returnable */}
              <section className="refund-nonreturn">
                <h3>2. Non-Returnable Items</h3>
                <ul>
                  <li>Innerwear and hygiene-sensitive products</li>
                  <li>Customized or personalized items</li>
                  <li>Clearance or final sale products</li>
                </ul>
                <p>Please check product details before purchasing.</p>
              </section>

              {/* Process */}
              <section className="refund-returnprocess">
                <h3>3. Return Process</h3>
                <ul>
                  <li>Log in to your Vastrika account</li>
                  <li>Go to <strong>My Orders</strong></li>
                  <li>Select the product and click <strong>Request Return</strong></li>
                  <li>Choose the reason and submit your request</li>
                </ul>
                <p>
                  Once approved, a pickup will be scheduled or you may be asked
                  to ship the product to our return facility.
                </p>
              </section>

              {/* Refund */}
              <section className="refund-refundprocess">
                <h3>4. Refund Process</h3>
                <p>After quality inspection:</p>
                <ul>
                  <li>Refunds are processed within <strong>5–7 business days</strong></li>
                  <li>Amount is credited to the original payment method</li>
                  <li>
                    COD refunds may be issued via bank transfer or store credit
                  </li>
                </ul>
                <p>
                  Timelines may vary depending on your bank or payment provider.
                </p>
              </section>

              {/* Exchange */}
              <section className="refund-exchangepolicy">
                <h3>5. Exchange Policy</h3>
                <p>We offer exchanges for:</p>
                <ul>
                  <li>Size-related issues</li>
                  <li>Defective or damaged products</li>
                </ul>
                <p>Subject to availability of stock.</p>
              </section>

              {/* Damaged */}
              <section className="refund-product">
                <h3>6. Damaged or Incorrect Products</h3>
                <ul>
                  <li>Report within <strong>48 hours of delivery</strong></li>
                  <li>Provide clear images or videos</li>
                  <li>
                    Replacement or full refund will be processed after
                    verification
                  </li>
                </ul>
              </section>

              {/* Late refunds */}
              <section className="refund-late">
                <h3>7. Late or Missing Refunds</h3>
                <ul>
                  <li>Check your bank account</li>
                  <li>Contact your bank or payment provider</li>
                  <li>
                    Reach us at{" "}
                    <a href="mailto:support@vastrika.com" style={{ color: '#c5396a' }}>
                      support@vastrika.com
                    </a>
                  </li>
                </ul>
              </section>

              {/* Shipping */}
              <section className="refund-shipping">
                <h3>8. Return Shipping</h3>
                <ul>
                  <li>Free for defective or incorrect items</li>
                  <li>
                    For other returns, shipping charges may be deducted from the
                    refund
                  </li>
                  <li>Original shipping charges are non-refundable</li>
                </ul>
              </section>

              {/* Cancellation */}
              <section className="refund-cancel">
                <h3>9. Cancellation vs Return</h3>
                <p>
                  Orders can be cancelled before shipment as per our{" "}
                  <strong>Cancellation Policy</strong>. Once shipped, returns must
                  follow the process above.
                </p>
              </section>

              {/* Contact */}
              <section className="refund-contact">
                <h3>10. Contact Us</h3>
                <p>
                  Email:{" "}
                  <a href="mailto:support@vastrika.com">
                    support@vastrika.com
                  </a>
                  <br />
                  Phone: <a href="tel:+911234567890">+91 12345 67890</a>
                  <br />
                  Support Hours: Monday – Saturday (10:00 AM – 6:00 PM)
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