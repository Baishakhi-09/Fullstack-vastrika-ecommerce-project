import React, { useEffect } from 'react'
import { updateMeta, updateOG } from '../utils/updateOG';
import CheckoutHeader from '../components/Productcard/checkout/CheckoutHeader';
// import { useNavigate } from "react-router-dom";
// import { useAuth } from "../context/AuthContext";

export default function Address() {
  // const navigate = useNavigate();
  // const { isLoggedIn, loading } = useAuth();
  // const [addresses, setAddresses] = useState([]);
  // const [selectedAddress, setSelectedAddress] = useState(null);

  //  const API_BASE = "http://127.0.0.1:8000/api";

  useEffect(() => {
    updateMeta({
      title: "Delivery Address | Vastrika",
      description:
        "Add or Select a delivery address to receive your vastrika order",
    });
            
    updateOG({
      title: "Delivery Address | Vastrika",
      description:
        "Add or Select a delivery address to receive your vastrika order",
      image: "/assets/image/logo/vastrika-logo.png",
      url: "/",
    });
            
  }, []);

  // ------------------ AUTH GUARD ------------------ //
  // useEffect(() => {
  //   if (!loading && !isLoggedIn) {
  //     navigate("/login");
  //   }
  // }, [isLoggedIn, loading, navigate]);

  // ------------------ FETCH ADDRESSES ------------------ //
  // useEffect(() => {
  //   const fetchAddresses = async () => {
  //     try {
  //       const res = await fetch(`${API_BASE}/address/`, {
  //         credentials: "include",
  //       });

  //       if (!res.ok) throw new Error("Failed to fetch addresses");

  //       const data = await res.json();
  //       setAddresses(data || []);
  //     } catch (err) {
  //       console.error("Address fetch error:", err);
  //     }
  //   };

  //   fetchAddresses();
  // }, []);

  // ------------------ CONTINUE ------------------ //
  // const handleContinue = () => {
  //   if (!selectedAddress) {
  //     alert("Please select an address");
  //     return;
  //   }

  //   navigate("/checkout/payment", {
  //     state: { address: selectedAddress },
  //   });
  // };

  return (
    <div>
      <CheckoutHeader step="ADDRESS"/>
    </div>
  )
}

//   // ------------------ UI ------------------ //
//   return (
//     <div className="checkout-layout">
//       <CheckoutHeader step="ADDRESS" />

//       <div className="checkout-container">
//         <h2>Select Delivery Address</h2>

//         {/* Address List */}
//         <div className="address-list">
//           {addresses.length === 0 ? (
//             <p>No addresses found. Please add one.</p>
//           ) : (
//             addresses.map((addr) => (
//               <div
//                 key={addr.id}
//                 className={`address-card ${
//                   selectedAddress?.id === addr.id ? "active" : ""
//                 }`}
//                 onClick={() => setSelectedAddress(addr)}
//               >
//                 <p><b>{addr.name}</b></p>
//                 <p>{addr.address_line}</p>
//                 <p>{addr.city}, {addr.state} - {addr.pincode}</p>
//                 <p>Phone: {addr.phone}</p>
//               </div>
//             ))
//           )}
//         </div>

//         {/* Actions */}
//         <div className="checkout-actions">
//           <button
//             className="add-address-btn"
//             onClick={() => navigate("/account/address")}
//           >
//             + Add New Address
//           </button>

//           <button
//             className="continue-btn"
//             onClick={handleContinue}
//             disabled={!selectedAddress}
//           >
//             Continue to Payment
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// }