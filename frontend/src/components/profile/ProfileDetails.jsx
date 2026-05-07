import React, { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { getCountries } from "@countrystatecity/countries-browser";

const showValue = (value, field = "") => {
    if (value === null || value === undefined || value === "") {
        return "— Not Added —";
    }
    if (field === "gender") {
        return value.charAt(0).toUpperCase() + value.slice(1);
    }
    return value;
}

const formatPhone = (phone, countries = "") => {
    if (!phone) return "— Not Added —";
    
    const clean = String(phone).replace(/\D/g, ""); // digits only

    const matched = countries
        .map(c => String(c.phonecode))
        .sort((a, b) => b.length - a.length) // longest first
        .find(code => clean.startsWith(code));
    
    if (!matched) return phone;

    const number = clean.slice(matched.length);

    return `+${matched} ${number}`;
};

export default function ProfileDetails({ onEdit }) {

    const { user, loading } = useAuth();
    const [countries, setCountries] = useState([]);

    useEffect(() => {
        const loadCountries = async () => {
            try {
                const countryList = await getCountries();
                setCountries(Array.isArray(countryList) ? countryList : []);
            } catch (error) {
                console.error("Failed to load countries:", error);
                setCountries([]);
            }
        };

        loadCountries();
    }, []);

    // Loading State
    if (loading) {
        return <div className="profile-loading">Loading profile...</div>;
    }

    if (!user) {
        return <div className="profile-error">Unable to load profile</div>;
    }

    return (
        <div className="profile-details">
            <h3>Profile Details</h3>
            <hr />

            <div className="detail">
                <div className="profile-row">
                    <span className="label">Full Name</span>
                    <span className="value">{showValue(user?.first_name)}</span>
                </div>

                <div className="profile-row">
                    <span className="label">Email</span>
                    <span className="value">{showValue(user?.email)}</span>
                </div>

                <div className="profile-row">
                    <span className="label">Mobile Number</span>
                    <span className="value">{formatPhone(user?.phone, countries)}</span>
                </div>

                <div className="profile-row">
                    <span className="label">Alternate Number</span>
                    <span className="value">{formatPhone(user?.alternate_phone, countries)}</span>
                </div>

                <div className="profile-row">
                    <span className="label">Gender</span>
                    <span className="value">{showValue(user.gender, "gender")}</span>
                </div>

                <div className="profile-row">
                    <span className="label">Address Line 1</span>
                    <span className="value">{showValue(user?.address_line_1)}</span>
                </div>

                <div className="profile-row">
                    <span className="label">Address Line 2</span>
                    <span className="value">{showValue(user?.address_line_2)}</span>
                </div>

                <div className="profile-row">
                    <span className="label">City</span>
                    <span className="value">{showValue(user?.city)}</span>
                </div>

                <div className="profile-row">
                    <span className="label">State</span>
                    <span className="value">{showValue(user?.state)}</span>
                </div>

                <div className="profile-row">
                    <span className="label">Pincode</span>
                    <span className="value">{showValue(user?.pincode)}</span>
                </div>

                <div className="profile-row">
                    <span className="label">Country</span>
                    <span className="value">{showValue(user?.country)}</span>
                </div>
            </div>

            <button className="edit-btn--profile" onClick={onEdit}>Edit Profile</button>
        </div>
    );
}