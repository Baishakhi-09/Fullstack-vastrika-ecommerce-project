import { useMemo } from "react";
import { useCart } from "../../../context/CartContext";
import CartItem from "./CartItem";

const CartList = () => {
    const { cart = [] } = useCart();

    // Memoized selected items count
    const selectedCount = useMemo(
        () => cart.filter((item) => item.selected).length,
        [cart]
    );

    // Empty cart
    if (cart.length === 0) {
        return (
            <div className="cart-empty" role="region" aria-label="Empty cart">
                <h2>Your Cart is Empty</h2>
                <p>Add items to get started.</p>
            </div>
        );
    }

    return (
        <section className="cart-list" aria-label="Shopping cart">

            {/* Header */}
            <div className="cart-header">
                <h2>Shopping Cart</h2>
                <p className="cart--items-selected">
                    {selectedCount} {selectedCount === 1 ? "Item" : "Items"} Selected
                </p>
            </div>

            {/* Cart Items */}
            <div className="cart-items">
                {cart.map((item) => (
                    <CartItem key={item.id} item={item} />
                ))}
            </div>

        </section>
    );
};

export default CartList;