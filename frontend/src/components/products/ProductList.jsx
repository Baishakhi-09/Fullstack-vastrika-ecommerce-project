import React, { useEffect, useState } from "react";
import axios from "axios";

export default function ProductList() {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const controller = new AbortController();

        const fetchProducts = async () => {
            try {
                const res = await axios.get(
                    "http://127.0.0.1:8000/api/products/",
                    {
                        withCredentials: true, // important for cookie auth
                        signal: controller.signal,
                    }
                );

                setProducts(res.data || []);
            } catch (err) {
                if (err.name !== "CanceledError") {
                    console.error("API Error:", err);
                    setError("Unable to load products. Please try again later.");
                }
            } finally {
                setLoading(false);
            }
        };

        fetchProducts();

        return () => controller.abort();
    }, []);

    const formatPrice = (value) =>
        new Intl.NumberFormat("en-IN").format(value || 0);

    // Loading State
    if (loading) {
        return (
            <div className="text-center p-10">
                <p>Loading products...</p>
            </div>
        );
    }

    // Error State
    if (error) {
        return (
            <div className="text-center text-red-500 p-10">
                <p>{error}</p>
            </div>
        );
    }

    // Empty State
    if (products.length === 0) {
        return (
            <div className="text-center p-10">
                <h2>No products found</h2>
                <p>Please check back later.</p>
            </div>
        );
    }

    return (
        <section className="container mx-auto p-4" aria-label="Product list">
            <h1 className="text-3xl font-bold mb-6">Our Products</h1>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {products.map((product) => (
                    <article key={product.id} className="border rounded-lg p-4 shadow-sm hover:shadow-md transition">
                        {/* Image */}
                        <img src={product.image || "/placeholder.png"} alt={product.name || "Product"} className="h-48 w-full object-cover rounded-md mb-4" />

                        {/* Info */}
                        <h2 className="text-lg font-semibold">
                            {product.name || "Unnamed Product"}
                        </h2>

                        <p className="text-gray-600 mb-2">
                            ₹{formatPrice(product.price)}
                        </p>

                        {/* CTA */}
                        <button type="button" className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 w-full" aria-label={`Add ${product.name} to cart`}>
                            Add to Cart
                        </button>
                    </article>
                ))}
            </div>
        </section>
    );
}