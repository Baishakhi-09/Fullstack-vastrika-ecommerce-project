import { useCart } from "../../../context/CartContext";

const CartItem = ({ item }) => {
    const { updateQty, toggleSelect, removeItem } = useCart();

    if (!item) return null;

    const { id, image, brand, name, size, qty, price, mrp, discount, selected, } = item;

    const formatPrice = (value) =>
        new Intl.NumberFormat("en-IN").format(value || 0);

    return (
        <div className="cart-item" role="group" aria-label={`Cart item ${name}`}>

            {/* Select Checkbox */}
            <input type="checkbox" checked={!!selected} onChange={() => toggleSelect(id)} aria-label={`Select ${name}`} />

            {/* Product Image */}
            <img src={image || "/placeholder.png"} alt={name || "Product image"} className="cart-item-image" />

            {/* Details */}
            <div className="cart-item-details">
                <h4 className="brand">{brand}</h4>
                <p className="name">{name}</p>

                <div className="meta">
                    <span>Size: {size || "N/A"}</span>

                    {/* Quantity Selector */}
                    <label>
                        Qty:
                        <select value={qty} onChange={(e) => updateQty(id, Number(e.target.value))} aria-label="Select quantity">
                            {[1, 2, 3, 4, 5].map((q) => (
                                <option key={q} value={q}>{q}</option>
                            ))}
                        </select>
                    </label>
                </div>

                {/* Pricing */}
                <div className="price-section">
                    <span className="price">₹{formatPrice(price)}</span>

                    {mrp && (
                        <span className="mrp">₹{formatPrice(mrp)}</span>
                    )}

                    {discount && (
                        <span className="discount">{discount} OFF</span>
                    )}
                </div>

                {/* Actions */}
                <div className="actions">
                    <button type="button" className="remove-btn" onClick={() => removeItem(id)} aria-label={`Remove ${name} from cart`}>Remove</button>
                </div>
            </div>
        </div>
    );
};

export default CartItem;