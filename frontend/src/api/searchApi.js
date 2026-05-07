// ---------------- SEARCH PRODUCTS (API BASED) ---------------- //
export const searchProducts = async (query) => {
    if (!query || query.trim() === "") return [];

    try {
        const response = await fetch(
            `http://127.0.0.1:8000/api/products/search/?q=${encodeURIComponent(query)}`,
            {
                method: "GET",
                credentials: "include",
            }
        );

        if (!response.ok) {
            throw new Error("Failed to fetch products");
        }

        const data = await response.json();
        return data.results || [];
    } catch (error) {
        console.error("Search error:", error);
        return [];
    }
};