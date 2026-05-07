import { useMemo } from "react";
import { useCart } from "../../../context/CartContext";

const CartSummary = () => {
    const { cart = [] } = useCart();

    // Memoized calculations
    const {
        selectedItems,
        totalMRP,
        totalAmount,
        totalDiscount,
        deliveryCharge,
        finalAmount,
    } = useMemo(() => {
        const selected = cart.filter((i) => i.selected);

        const mrp = selected.reduce((sum, i) => sum + (i.mrp || 0) * i.qty, 0);

        const amount = selected.reduce(
            (sum, i) => sum + (i.price || 0) * i.qty, 0
        );

        const discount = mrp - amount;

        // Delivery logic
        const delivery = amount > 999 || amount === 0 ? 0 : 99;

        return {
            selectedItems: selected,
            totalMRP: mrp,
            totalAmount: amount,
            totalDiscount: discount,
            deliveryCharge: delivery,
            finalAmount: amount + delivery,
        };
    }, [cart]);

    const formatPrice = (value) =>
        new Intl.NumberFormat("en-IN").format(value || 0);

    return (
        <aside className="price-box" aria-label="Price details">
            <h3>PRICE DETAILS</h3>

            {/* Total MRP */}
            <div className="price-row">
                <span>Total MRP</span>
                <span>₹{formatPrice(totalMRP)}</span>
            </div>

            {/* Discount */}
            <div className="price-row discount-row">
                <span>Discount</span>
                <span className="discount">- ₹{formatPrice(totalDiscount)}</span>
            </div>

            {/* Delivery */}
            <div className="price-row">
                <span>Delivery Charge</span>
                <span>
                    {deliveryCharge === 0 ? (
                        <span className="free">FREE</span>
                    ) : (
                        `₹${formatPrice(deliveryCharge)}`
                    )}
                </span>
            </div>

            <hr/>

            {/* Final Amount */}
            <div className="price-row total">
                <span>Total Amount</span>
                <span>₹{formatPrice(finalAmount)}</span>
            </div>

            {/* Agreement */}
            <p className="cart-agree">
                By placing the order, you agree to Vastrika's{" "}
                <a href="/terms-and-conditions" target="_blank" rel="noopener noreferrer" style={{ color: '#C5396A' }}>
                    Terms of Use
                </a>{" "}
                and{" "}
                <a href="/privacy-policy" target="_blank" rel="noopener noreferrer">
                    Privacy Policy
                </a>
            </p>

            {/* CTA Button */}
            <button className="place-order" disabled={selectedItems.length === 0} aria-disabled={selectedItems.length === 0}>
                {selectedItems.length === 0
                    ? "Select items to continue"
                    : "Proceed to Buy"}
            </button>

        </aside>
    );
};

export default CartSummary;