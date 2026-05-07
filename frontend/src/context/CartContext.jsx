import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useAuth } from "./AuthContext";

const CartContext = createContext();

const PRODUCTS_API =
  import.meta.env.VITE_PRODUCTS_API || "http://127.0.0.1:8000/api/products";

export const CartProvider = ({ children }) => {

  const { isLoggedIn, loading: authLoading } = useAuth();

  const [cart, setCart] = useState([]);
  const [wishlist, setWishlist] = useState([]);
  const [loading, setLoading] = useState(true);

  const [address, setAddress] = useState({
    pincode: "",
    city: "",
    state: "",
  });

  const normalizeListResponse = (data) => {
    if (Array.isArray(data)) return data;
    return data.results || data.items || [];
  };

  // ------------------ FETCH CART ------------------ //
  const fetchCart = async () => {
    try {
      const res = await fetch(`${PRODUCTS_API}/cart/`, {
        method: "GET",
        credentials: "include",
      });

      if (res.status === 401) {
        setCart([]);
        return false;
      }

      if (res.status === 404) {
        setCart([]);
        return false;
      }

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Failed to fetch cart (${res.status})`);
      }

      const data = await res.json();
      setCart(normalizeListResponse(data));
      return true;
    } catch (error) {
      console.error("Cart fetch error:", error);
      setCart([]);
      return false;
    }
  };

  // ------------------ FETCH WISHLIST ------------------ //
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
      setWishlist(normalizeListResponse(data));
      return true;
    } catch (error) {
      console.error("Wishlist fetch error:", error);
      setWishlist([]);
      return false;
    }
  };

  // ------------------ INIT LOAD ------------------ //
  useEffect(() => {
    const init = async () => {
      try {
        if (authLoading) return;

        if (isLoggedIn) {
          await Promise.all([fetchCart(), fetchWishlist()]);
        } else {
          setCart([]);
          setWishlist([]);
        }
      } finally {
        setLoading(false);
      }
    };

    init();
  }, [authLoading, isLoggedIn]);

  // ------------------ CART ACTIONS ------------------ //
  const addToCart = async (product, qty = 1) => {
    if (!isLoggedIn) return false;

    try {
      const res = await fetch(`${PRODUCTS_API}/cart/`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          product_id: product.id,
          qty: 1,
        }),
      });

      if (res.status === 401 || res.status === 404) {
        return false;
      }

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Add to cart failed");
      }

      await fetchCart();
      return true;
    } catch (error) {
      console.error("Add cart error:", error);
      return false;
    }
  };

  const updateQty = async (id, qty) => {
    try {
      const res = await fetch(`${PRODUCTS_API}/cart/${id}/`, {
        method: "PUT",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ qty }),
      });

      if (res.status === 401 || res.status === 404) {
        return false;
      }

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Update failed");
      }

      setCart((prev) =>
        prev.map((item) =>
          item.id === id ? { ...item, qty } : item
        )
      );

      return true;
    } catch (error) {
      console.error("Update qty error:", error);
      return false;
    }
  };

  // ------------------ Remove Item ------------------ //
  const removeItem = async (id) => {
    try {
      const res = await fetch(`${PRODUCTS_API}/cart/${id}/`, {
        method: "DELETE",
        credentials: "include",
      });

      if (res.status === 401 || res.status === 404) {
        return false;
      }

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Remove failed");
      }

      setCart((prev) => prev.filter((item) => item.id !== id));
      return true;
    } catch (error) {
      console.error("Remove cart error:", error);
      return false;
    }
  };

  // ------------------ Clear Cart ------------------ //
  const clearCart = async () => {
    try {
      const items = [...cart];
      const results = await Promise.all(
        items.map((item) =>
          fetch(`${PRODUCTS_API}/cart/${item.id}/`, {
            method: "DELETE",
            credentials: "include",
          })
        )
      );

      const hasError = results.some((res) => !res.ok && res.status !== 404);
      if (hasError) {
        throw new Error("Clear failed");
      }

      setCart([]);
      return true;
    } catch (error) {
      console.error("Clear cart error:", error);
      return false;
    }
  };

  const toggleSelect = (id) => {
    setCart((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, selected: !item.selected } : item
      )
    );
  };

  // ------------------ WISHLIST ------------------ //
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
        throw new Error(text || "Wishlist add failed");
      }

      await fetchWishlist();
      return true;
    } catch (error) {
      console.error("Wishlist add error:", error);
      return false;
    }
  };

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
        throw new Error(text || "Wishlist remove failed");
      }

      setWishlist((prev) => prev.filter((item) => item.id !== id));
      return true;
    } catch (error) {
      console.error("Wishlist remove error:", error);
      return false;
    }
  };

  // ------------------ ADDRESS ------------------ //
  const updateAddress = (newAddress) => {
    setAddress(newAddress);
  };

  // ------------------ DERIVED ------------------ //
  const cartCount = useMemo(
    () => cart.reduce((sum, item) => sum + (item.qty || 0), 0),
    [cart]
  );

  const wishlistCount = useMemo(
    () => wishlist.length,
    [wishlist]
  );

  const selectedItems = useMemo(
    () => cart.filter((item) => item.selected),
    [cart]
  );

  return (
    <CartContext.Provider value={{ cart, wishlist, loading, addToCart, updateQty, removeItem, clearCart, toggleSelect, addToWishlist, removeFromWishlist, address, setAddress, updateAddress, cartCount, wishlistCount, selectedItems, fetchCart, fetchWishlist, }}>
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => {
  const context = useContext(CartContext);

  if (!context) {
    throw new Error("useCart must be used inside CartProvider");
  }

  return context;
};