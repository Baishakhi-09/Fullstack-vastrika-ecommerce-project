import { useEffect, useState, useRef } from "react";
import { searchProducts } from "../api/searchApi";

export const useSearch = () => {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const debounceRef = useRef(null);

    useEffect(() => {
        // Reset when empty
        if (!query.trim()) {
            setResults([]);
            setLoading(false);
            return;
        }

        // Clear previous debounce
        if (debounceRef.current) {
            clearTimeout(debounceRef.current);
        }

        // Debounce API call
        debounceRef.current = setTimeout(async () => {
            try {
                setLoading(true);
                setError(null);

                const data = await searchProducts(query);

                // Ensure valid array response
                setResults(Array.isArray(data) ? data : []);

            } catch (err) {
                console.error("Search error:", err);
                setError("Failed to fetch results");
                setResults([]);
            } finally {
                setLoading(false);
            }
        }, 400); // slightly improved debounce timing

        // Cleanup
        return () => clearTimeout(debounceRef.current);

    }, [query]);

    return { query, setQuery, results, loading, error };
};