import React, { useEffect } from "react";
import { updateMeta, updateOG } from "../../utils/updateOG";
import Header from "../../components/header/Header";
import Footer from "../../components/footer/Footer";

export default function ShippingPolicy() {
  const today = new Date().toLocaleDateString("en-IN", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  useEffect(() => {
    updateMeta({
      title: "Shipping Policy | Vastrika",
      description:
        "Learn about Vastrika’s shipping timelines, delivery charges, order tracking, and nationwide delivery services across India.",
    });

    updateOG({
      title: "Shipping Policy | Vastrika",
      description:
        "Learn about Vastrika’s shipping timelines, delivery charges, order tracking, and nationwide delivery services across India.",
      image: window.location.origin + "/assets/image/logo/vastrika-logo.png",
      url: window.location.origin + "/shipping-policy",
    });
  }, []);

  return (
    <>
      <Header />

      <main className="app-layout">
        <div className="main-content">
          <section className="shipping-wrapper">
            <div className="shipping-container">

              {/* Heading */}
              <header className="shipping-heading">
                <h1>Shipping Policy</h1>
                <p className="policy-date">
                  <strong>Last Updated:</strong> {today}
                </p>
                <p>
                  At <strong>Vastrika</strong>, we are committed to delivering your
                  fashion and lifestyle products safely and on time. This policy
                  outlines our shipping process, delivery timelines, and charges.
                </p>
              </header>

              {/* Processing */}
              <section className="shipping-order">
                <h3>1. Order Processing Time</h3>
                <ul>
                  <li>Orders are processed within <strong>1–3 business days</strong></li>
                  <li>Excludes Sundays and public holidays</li>
                  <li>Order confirmation is sent via email/SMS</li>
                  <li>Processing may be delayed during sales or festive periods</li>
                </ul>
              </section>

              {/* Charges */}
              <section className="shipping-charges">
                <h3>2. Shipping Charges</h3>
                <ul>
                  <li><strong>Free shipping</strong> on orders above ₹5000</li>
                  <li>₹500 shipping fee for orders below ₹5000</li>
                  <li>Final charges are displayed at checkout</li>
                </ul>
              </section>

              {/* Delivery */}
              <section className="shipping-delivery">
                <h3>3. Delivery Timeline</h3>
                <p>Estimated delivery time:</p>
                <ul>
                  <li><strong>Metro Cities:</strong> 3–5 business days</li>
                  <li><strong>Non-Metro Cities:</strong> 5–7 business days</li>
                  <li><strong>Remote Areas:</strong> 7–10 business days</li>
                </ul>
                <p>
                  Delays may occur due to weather conditions, courier issues, or
                  high demand periods.
                </p>
              </section>

              {/* Tracking */}
              <section className="shipping-tracking">
                <h3>4. Order Tracking</h3>
                <ul>
                  <li>Tracking details are shared once the order is shipped</li>
                  <li>Track your order in real-time using the tracking link</li>
                  <li>
                    For assistance, contact{" "}
                    <a href="mailto:support@vastrika.com">
                      support@vastrika.com
                    </a>
                  </li>
                </ul>
              </section>

              {/* Locations */}
              <section className="shipping-location">
                <h3>5. Shipping Locations</h3>
                <p>
                  We currently deliver across India. International shipping will
                  be introduced soon.
                </p>
                <p>
                  If your location is not serviceable, you will be notified during
                  checkout.
                </p>
              </section>

              {/* Delays */}
              <section className="shipping-shipment">
                <h3>6. Delayed or Lost Shipments</h3>
                <ul>
                  <li>Delays may occur due to courier or external factors</li>
                  <li>
                    Report delayed or missing orders within{" "}
                    <strong>7 days</strong> of expected delivery
                  </li>
                  <li>We will coordinate with the courier partner to resolve it</li>
                </ul>
              </section>

              {/* Address */}
              <section className="hipping-addressinformation">
                <h3>7. Incorrect Address</h3>
                <ul>
                  <li>Customers must provide accurate delivery details</li>
                  <li>Incorrect addresses may cause delays or returns</li>
                  <li>Re-shipping charges may apply</li>
                </ul>
              </section>

              {/* Damaged */}
              <section className="shipping-damaged">
                <h3>8. Damaged or Tampered Packages</h3>
                <ul>
                  <li>Do not accept visibly damaged packages</li>
                  <li>Report immediately with photos (if possible)</li>
                  <li>
                    Replacement/refund will be processed as per Return Policy
                  </li>
                </ul>
              </section>

              {/* Contact */}
              <section className="shipping-contact">
                <h3>9. Contact Us</h3>
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