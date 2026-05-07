import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useAuth } from "./AuthContext";

const WishlistContext = createContext();

const PRODUCTS_API =
  import.meta.env.VITE_PRODUCTS_API || "http://127.0.0.1:8000/api/products";

export const WishlistProvider = ({ children }) => {
  const { isLoggedIn, loading: authLoading } = useAuth();

  const [wishlist, setWishlist] = useState([]);
  const [loading, setLoading] = useState(true);

  // ------------------ FETCH FROM BACKEND ------------------ //
  const fetchWishlist = async () => {
    try {
      const res = await fetch(`${PRODUCTS_API}/wishlist/`, {
        method: "GET",
        credentials: "include",
      });

      if (res.status === 401) {
        setWishlist([]);
        return false;
      }

      if (res.status === 404) {
        setWishlist([]);
        return false;
      }

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Failed to fetch wishlist (${res.status})`);
      }

      const data = await res.json();
      const normalized = Array.isArray(data) ? data : data.results || data.items || [];

      setWishlist(normalized);
      return true;
    } catch (error) {
      console.error("Wishlist fetch error:", error);
      setWishlist([]);
      return false;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const init = async () => {
      if (authLoading) return;

      if (isLoggedIn) {
        setLoading(true);
        await fetchWishlist();
      } else {
        setWishlist([]);
        setLoading(false);
      }
    };

    init();
  }, [authLoading, isLoggedIn]);

  // ------------------ ADD ------------------ //
  const addToWishlist = async (product) => {
    if (!isLoggedIn) return false;

    try {
      const res = await fetch(`${PRODUCTS_API}/wishlist/`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ product_id: product.id }),
      });

      if (res.status === 401 || res.status === 404) {
        return false;
      }

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Failed to add to wishlist");
      }

      await fetchWishlist();
      return true;
    } catch (error) {
      console.error("Add wishlist error:", error);
      return false;
    }
  };

  // ------------------ REMOVE ------------------ //
  const removeFromWishlist = async (id) => {
    try {
      const res = await fetch(`${PRODUCTS_API}/wishlist/${id}/`, {
        method: "DELETE",
        credentials: "include",
      });

      if (res.status === 401 || res.status === 404) {
        return false;
      }

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Failed to remove from wishlist");
      }

      setWishlist((prev) => prev.filter((item) => item.id !== id));
      return true;
    } catch (error) {
      console.error("Remove wishlist error:", error);
      return false;
    }
  };

  // ------------------ TOGGLE ------------------ //
  const toggleWishlist = async (product) => {
    const exists = wishlist.some((item) => item.product_id === product.id);

    if (exists) {
      const item = wishlist.find((i) => i.product_id === product.id);
      if (item) {
        await removeFromWishlist(item.id);
      }
    } else {
      await addToWishlist(product);
    }
  };

  // ------------------ CHECK ------------------ //
  const isInWishlist = (productId) => {
    return wishlist.some((item) => item.product_id === productId);
  };

  // ------------------ DERIVED ------------------ //
  const wishlistCount = useMemo(() => wishlist.length, [wishlist]);

  return (
    <WishlistContext.Provider
      value={{ wishlist, loading, fetchWishlist, addToWishlist, removeFromWishlist, toggleWishlist, isInWishlist, wishlistCount, }}>
      {children}
    </WishlistContext.Provider>
  );
};

export const useWishlist = () => {
  const context = useContext(WishlistContext);

  if (!context) {
    throw new Error("useWishlist must be used inside WishlistProvider");
  }

  return context;
};