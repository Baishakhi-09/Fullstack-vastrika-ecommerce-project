import React, { useEffect } from 'react'
import { updateMeta, updateOG } from '../utils/updateOG';
import CheckoutHeader from '../components/Productcard/checkout/CheckoutHeader';

export default function Payment() {

  useEffect(() => {
    updateMeta({
      title: "Secure Payment | Vastrika",
      description:
        "Complete your purchase securely using trusted payment methods",
    });
              
    updateOG({
      title: "Secure Payment | Vastrika",
      description:
        "Complete your purchase securely using trusted payment methods",
      image: "/assets/image/logo/vastrika-logo.png",
      url: "/",
    });
              
  }, []);

  return (
    <div>
      <CheckoutHeader step="PAYMENT" />
    </div>
  )
}