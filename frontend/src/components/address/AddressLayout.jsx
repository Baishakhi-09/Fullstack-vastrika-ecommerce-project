import React from 'react';
import ProfileSidebar from '../profile/ProfileSidebar';
import AddressDetails from './AddressDetails';

export default function AddressLayout() {
    return (
        <main className="app-layout">
            <div className="main-content">
                <section className="profile-wrapper--layout">
                    <div className="profile-container">
                        <div className="page-page--profile">
                            <ProfileSidebar />

                            <div className="profile-content">
                                <AddressDetails />
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </main>
    );
}