import { Link } from "react-router-dom";
import logo from "../../../assets/image/logo/vastrika-logo.png";

const steps = ["BAG", "ADDRESS", "PAYMENT"];

const CheckoutHeader = ({ activeStep = "BAG" }) => {
    const currentIndex = steps.indexOf(activeStep);

    return (
        <header className="checkout-header" role="banner">

            {/* Logo */}
            <div className="checkout-logo">
                <Link to="/" aria-label="Go to homepage">
                    <img src={logo} alt="Vastrika Logo" />
                </Link>
            </div>

            {/* Steps */}
            <nav className="checkout-steps" aria-label="Checkout Progress">
                {steps.map((step, index) => {
                    const isActive = step === activeStep;
                    const isCompleted = index < currentIndex;

                    return (
                        <div key={step} className="step-wrapper">
                            
                            <span className={`step ${isActive ? "active" : ""}
                                ${isCompleted ? "completed" : ""}
                                `} aria-current={isActive ? "step" : undefined}>
                                    {step}
                            </span>

                            {/* Divider */}
                            {index < steps.length - 1 && (
                                <span className="divider" aria-hidden="true"></span>
                            )}
                        </div>
                    );
                })}
            </nav>

        </header>
    );
};

export default CheckoutHeader;