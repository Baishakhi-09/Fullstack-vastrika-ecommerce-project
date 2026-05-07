import { useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";

import Header from "../components/header/Header";
import Footer from "../components/footer/Footer";

import { useWishlist } from "../context/WishlistContext";
import { updateMeta, updateOG } from "../utils/updateOG";

import empty from "../assets/image/emptylist.png";

const Wishlist = () => {
    const { wishlist, removeFromWishlist } = useWishlist();
    const navigate = useNavigate();

    // ---------------- SEO ---------------- //
    useEffect(() => {
        updateMeta({
            title: "My Wishlist | Save Your Favorite Products – Vastrika",
            description:
                "View and manage your wishlist on Vastrika. Save your favorite fashion and lifestyle products and shop them later easily.",
        });

        updateOG({
            title: "My Wishlist | Save Your Favorite Products – Vastrika",
            description:
                "View and manage your wishlist on Vastrika. Save your favorite fashion and lifestyle products and shop them later easily.",
            image: `${window.location.origin}/assets/image/logo/vastrika-logo.png`,
            url: `${window.location.origin}/wishlist`,
        });

        // Clean keyword handling (no duplicate injection)
        let metaKeywords = document.querySelector('meta[name="keywords"]');
        if (!metaKeywords) {
            metaKeywords = document.createElement("meta");
            metaKeywords.name = "keywords";
            document.head.appendChild(metaKeywords);
        }

        metaKeywords.content =
            "wishlist fashion India, save products online, Vastrika wishlist, fashion wishlist, save for later shopping";
    }, []);

    return (
        <>
            <Header />

            <main className="app-layout">
                <section className="main-content">
                    <div className="wish-wrapper">
                        <div className="wish-container">

                            {/* Header */}
                            <div className="wish">
                                <h2>
                                    Shopping List{" "}
                                    <span>({wishlist?.length || 0})</span>
                                </h2>

                                 {/* ---------------- EMPTY STATE ---------------- */}
                                {wishlist.length === 0 ? (
                                    <div className="empty-wishlist">
                                        <img src={empty} alt="Empty wishlist" loading="lazy" />
                                        <h3>
                                            {/* Your wishlist is empty */}
                                            No items in your Wishlist
                                        </h3>
                                        <p>
                                            {/* Browse products and save your favorites here. */}
                                            Start adding products you love. 
                                            <Link className="primary-btn" onClick={() => navigate("/")}>Continue Shopping</Link>
                                        </p>
                                    </div>
                                ) : (
                                    /* ---------------- LIST ---------------- */
                                    // <div className="wishlist-grid">
                                    <div className="wishlist-page">
                                        {wishlist.map((item) => (
                                            <div className="wishlist-item" key={item.id}>
                                                
                                                {/* Image */}
                                                <div
                                                    className="wishlist-image"
                                                    onClick={() => navigate(`/product/${item.id}`)}
                                                    style={{ cursor: "pointer" }}>
                                                    <img src={item.image} alt={item.title || "Product"} loading="lazy" />
                                                </div>

                                                {/* Details */}
                                                <div className="wishlist-info">
                                                    <h4>{item.title}</h4>

                                                    <p className="price">
                                                        ₹{item.price}
                                                        {item.mrp && (
                                                            <span className="mrp">
                                                                ₹{item.mrp}
                                                            </span>
                                                        )}
                                                        {item.discount && (
                                                            <span className="discount">
                                                                {item.discount}% OFF
                                                            </span>
                                                        )}
                                                    </p>
                                                </div>

                                                {/* Actions */}
                                                <div className="wishlist-actions">
                                                    <button
                                                        className="remove-btn"
                                                        onClick={() => removeFromWishlist(item.id)}
                                                    >
                                                        Remove
                                                    </button>

                                                    <button
                                                        className="move-btn"
                                                        onClick={() => navigate(`/product/${item.id}`)}
                                                    >
                                                        View Product
                                                    </button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </section>
            </main>

            <Footer />
        </>
    );
};

export default Wishlist;