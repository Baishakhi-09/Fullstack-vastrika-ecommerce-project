import React, { useState } from 'react';
import emptyAddress from '../../assets/image/icon/no-address-icon.png';
import AddressModels from './AddressModels';

export default function AddressDetails() {
  const [isOpen, setIsOpen] = useState(false);

  const handleOpen = () => setIsOpen(true);
  const handleClose = () => setIsOpen(false);

  return (
    <>
      <div className="empty-state">
        <img src={emptyAddress} alt="No Address available" />
        <p>Add your home and office addresses for faster the checkout process.</p>

        <button onClick={handleOpen} className="address--btn" aria-label="Add New Address">+ Add New Address</button>

        <AddressModels isOpen={isOpen} onClose={handleClose} onSave={(data) => { console.log("Saved Address:", data); }} /> 
      </div>
    </>
  );
}