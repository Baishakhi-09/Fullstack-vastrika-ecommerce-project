import React, { useEffect } from "react";
import ProfileLayout from "../components/profile/ProfileLayout";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import Loader from "../components/loader/Loader";
import { updateMeta, updateOG } from "../utils/updateOG";

export default function Profile() {

  useEffect(() => {
    updateMeta({
      title: "My Profile | Vastrika – Manage Your Account, Orders & Wishlist",
      description:
        "Access your Vastrika profile to manage personal details, track orders, update addresses, and explore your wishlist. Enjoy a seamless fashion shopping experience with Vastrika.",
      keywords: "Vastrika profile, my account Vastrika, manage orders, wishlist fashion, user dashboard Vastrika, online fashion profile India",
    });
            
    updateOG({
      title: "My Profile | Vastrika – Manage Your Account, Orders & Wishlist",
      description:
        "Access your Vastrika profile to manage personal details, track orders, update addresses, and explore your wishlist. Enjoy a seamless fashion shopping experience with Vastrika.",
        image: window.location.origin + "/assets/image/logo/vastrika-logo.png",
        url: window.location.origin + "/",
    });
            
  }, []);

  const { user, loading } = useAuth(); // include loading state
  const navigate = useNavigate();

  useEffect(() => {
    // Wait until auth check completes
    if (!loading && !user) {
      navigate("/login", { replace: true });
    }
  }, [user, loading, navigate]);

  if (loading) {
    return <Loader />
  }

  // Prevent render if not authenticated
  if (!user) return null;

  return (
    <div className="profile-page">
      <ProfileLayout user={user} />
    </div>
  );
}