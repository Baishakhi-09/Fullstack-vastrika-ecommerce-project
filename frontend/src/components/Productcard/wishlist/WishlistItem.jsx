import { useWishlist } from "../../../context/WishlistContext";

const WishlistItem = ({ product }) => {
    const { addToWishlist, removeFromWishlist, isInWishlist } = useWishlist();

    if (!product) return null;
    
    const { id, image, title, brand, price, mrp, } = product;

    const inWishlist = isInWishlist(id);

    const handleToggleWishlist = () => {
        inWishlist ? removeFromWishlist(id) : addToWishlist(product);
    };

    const formatPrice = (value) =>
        new Intl.NumberFormat("en-IN").format(value || 0);

    return (
        <div className="wishlist--product-card" role="group" aria-label={`Wishlist item ${title}`}>

            {/* Product Image */}
            <div className="wishlist-image">
                <img src={image || "/placeholder.png"} alt={title || "Product image"} />
            </div>

            {/* Product Info */}
            <div className="wishlist-details">
                <h4 className="brand">{brand}</h4>
                <p className="title">{title}</p>

                {/* Pricing */}
                <div className="price-section">
                    <span className="price">₹{formatPrice(price)}</span>
                    {mrp && (
                        <span className="mrp">₹{formatPrice(mrp)}</span>
                    )}
                </div>
            </div>

            {/* Actions */}
            <div className="wishlist-actions">
                <button type="button" className={`wishlist-btn ${inWishlist ? "active" : ""}`} onClick={handleToggleWishlist} aria-label={ inWishlist ? `Remove ${title} from wishlist` : `Add ${title} to wishlist` }>
                    {inWishlist ? "Remove" : "Move to Wishlist"}
                </button>
            </div>

        </div>
    );
};

export default WishlistItem;