import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function ProfileSidebar() {
    const { user } = useAuth();
    const location = useLocation();

    // Helper for active class
    const isActive = (path) => location.pathname === path;

    return (
        <>
        {/* <div className="profile-sidebar-wrapper"> */}

            {/* Account Header */}
            <div className="account-account--profile">
                <div className="account-heading--profile">Account</div>

                <p className="profile--username">
                    {user?.first_name || "Guest User"}
                </p>
            </div>

            {/* Sidebar Menu */}
            <nav className="profile-sidebar">
                <ul>
                    <li className={isActive("/profile") ? "active" : ""}>
                        <Link to="/profile">Profile</Link>
                    </li>

                    <li className={isActive("/orders") ? "active" : ""}>
                        <Link to="/orders">Orders & Returns</Link>
                    </li>

                    <li className={isActive("/account/address") ? "active" : ""}>
                        <Link to="/account/address">Addresses</Link>
                    </li>

                    <li>
                        <button className="delete-account-btn"
                            onClick={() => {
                                if (window.confirm("Are you sure you want to delete your account?")) {
                                    console.log("Delete account API call here");
                                }
                            }}>
                                Delete Account
                        </button>
                    </li>
                </ul>
            </nav>

        {/* </div> */}
        </>
    );
}