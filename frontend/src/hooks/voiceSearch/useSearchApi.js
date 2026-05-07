import { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8000/api";

export function useSearchApi(query) {

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Reset when query is empty
    if (!query || query.trim() === "") {
      setResults([]);
      setLoading(false);
      return;
    }

    const controller = new AbortController();

    // Debounce
    const delayDebounce = setTimeout(() => {
      const fetchData = async () => {
        setLoading(true);
        setError(null);

        try {
          const res = await fetch(
            `${API_BASE}/products/search/?q=${encodeURIComponent(query)}`,
            {
              method: "GET",
              credentials: "include", // cookie auth ready
              signal: controller.signal,
            }
          );

          if (!res.ok) throw new Error("Search failed");

          const data = await res.json();

          // Safe fallback
          setResults(Array.isArray(data.results) ? data.results : []);
        } catch (err) {
          if (err.name !== "AbortError") {
            console.error("Search error:", err);
            setError(err.message);
            setResults([]);
          }
        } finally {
          setLoading(false);
        }
      };

      fetchData();
    }, 400);

    return () => {
      clearTimeout(delayDebounce);
      controller.abort();
    };
  }, [query]);

  return { results, loading, error };
}