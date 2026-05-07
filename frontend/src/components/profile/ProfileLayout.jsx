import React, { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';

import ProfileDetails from './ProfileDetails';
import ProfileSidebar from './ProfileSidebar';
import EditProfile from './EditProfile';

import Header from '../header/Header';
import Footer from '../footer/Footer';

export default function ProfileLayout() {
    const { isLoggedIn, loading } = useAuth();
    const [isEditing, setIsEditing] = useState(false);

    useEffect(() => {
        if (isEditing) {
            const scrollY = window.scrollY;

            document.body.style.position = 'fixed';
            document.body.style.top = `-${scrollY}px`;
            document.body.style.left = '0';
            document.body.style.right = '0';
            document.body.style.overflow = 'hidden';
            document.body.style.width = '100%';
        } else {
            const scrollY = document.body.style.top;

            document.body.style.position = '';
            document.body.style.top = '';
            document.body.style.left = '';
            document.body.style.right = '';
            document.body.style.overflow = '';
            document.body.style.width = '';

            if (scrollY) {
                window.scrollTo(0, parseInt(scrollY || '0') * -1);
            }
        }

        return () => {
            document.body.style.position = '';
            document.body.style.top = '';
            document.body.style.left = '';
            document.body.style.right = '';
            document.body.style.overflow = '';
            document.body.style.width = '';
        };
    }, [isEditing]);

    // If not logged in
    if (!isLoggedIn) {
        return (
            <>
                <Header />
                <div className="auth-warning">
                    <h2>Please login to view your profile</h2>
                </div>
                <Footer />
            </>
        );
    }

    return (
        <>
            <Header />

            <div className="app-layout">
                <div className="main-content">
                    <div className="profile-wrapper--layout">
                        <div className="profile-container">
                            <div className="page-page--profile">
                                <div className="profile-sidebar-wrapper">

                                    {/* Sidebar */}
                                    <ProfileSidebar />

                                    {/* Content */}
                                    <div className="profile-content">
                                        <ProfileDetails onEdit={() => setIsEditing(true)} />
                                        {/* {isEditing ? (
                                            <EditProfile onCancel={() => setIsEditing(false)} />
                                        ) : (
                                            <ProfileDetails onEdit={() => setIsEditing(true)} />
                                        )} */}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {isEditing && (
                <div className="profile-modal-overlay" onClick={() => setIsEditing(false)}>
                    <div className="profile-modal-box" onClick={(e) => e.stopPropagation()}>
                        <div className="edit-profile-header">
                            <h2>Edit Profile</h2>
                            <button className="profile-modal-close" onClick={() => setIsEditing(false)} aria-label="Close edit profile popup" type="button">×</button>
                        </div>

                        <EditProfile onCancel={() => setIsEditing(false)} />
                    </div>
                </div>
            )}

            <Footer/>
        </>
    );
}