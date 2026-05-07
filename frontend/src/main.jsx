import React from 'react';
import { StrictMode } from 'react'
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

// Contexts
import { CartProvider } from './context/CartContext.jsx';
import { WishlistProvider } from './context/WishlistContext.jsx';
import { AuthProvider } from './context/AuthContext.jsx';

import ProtectedRoute from './components/ProtectedRoute.jsx';

// Pages
import Home from './pages/Home.jsx';
import Login from './pages/Login/Login.jsx';
import Signup from './pages/Login/Signup.jsx';
import Forgetpassword from './pages/Login/Forgetpassword.jsx';
import VerifyOTP from './pages/Login/VerifyOTP.jsx';
import ResetPassword from './pages/Login/ResetPassword.jsx';

import Wishlist from './pages/Wishlist.jsx';
import Cart from './pages/Cart.jsx';
import Address from './pages/Address.jsx';
import Payment from './pages/Payment.jsx';
import Profile from './pages/Profile.jsx';
import Index from './pages/account/Index.jsx';
import AddressPage from './pages/account/AddressPage.jsx';


import ShippingPolicy from './pages/legal/ShippingPolicy.jsx';
import CancellationPolicy from './pages/legal/CancellationPolicy.jsx';
import ReturnPolicy from './pages/legal/ReturnPolicy.jsx';
import PrivacyPolicy from './pages/legal/PrivacyPolicy.jsx';
import TermsConditions from './pages/legal/TermConditions.jsx';

import Error404 from './pages/Error404.jsx';
import { ToastContainer } from 'react-toastify';
import Product from './pages/Product/Product.jsx';

const root = ReactDOM.createRoot(document.getElementById('root'));
let allRoutes=createBrowserRouter(
  [
    {
      path:'/',
      element:<Home/>
    },

    // Auth
    { path:'login', element:<Login/> },
    { path:'signup', element:<Signup/> },
    { path:'forgot-password', element:<Forgetpassword/> },
    { path: 'forgot-password/verify-otp', element:<VerifyOTP/> },
    { path: 'reset-password', element:<ResetPassword/> },

    // Account
    { path:'my-account', element:<Index/> },
    {
      path:'profile',
      element: (
        <ProtectedRoute>
          <Profile/>
        </ProtectedRoute>
      ),
    },
    { path:'account/address', 
      element: (
        <ProtectedRoute>
          <AddressPage />
        </ProtectedRoute>
      ),
    },

    // Product
    // {
    //   path: "/products",
    //   element: <Product />,
    // },
    {
      path: "/products/:departmentSlug",
      element: <Product />,
    },
    {
      path: "/products/:departmentSlug/:sectionSlug",
      element: <Product />,
    },
    {
      path: "/products/:departmentSlug/:sectionSlug/:itemSlug",
      element: <Product />,
    },

    // Shopping
    { path:'wishlist', element:<Wishlist/> },
    { path:'cart', element:<Cart/> },
    { path:'address', element:<Address/> },
    { path:'payment', element:<Payment/> },

    // Legal
    { path:'terms-and-conditions', element:<TermsConditions/> },
    { path:'shipping-policy', element:<ShippingPolicy/> },
    { path:'cancellation-policy', element:<CancellationPolicy/> },
    { path:'return-and-refund-policy', element:<ReturnPolicy/> },
    { path:'privacy-policy', element:<PrivacyPolicy/> },

    // 404
    { path:'*', element:<Error404/> },
  ]
)

root.render(
  <StrictMode>
    <AuthProvider>
      <CartProvider>
        <WishlistProvider>
            <RouterProvider router={allRoutes}/>
            <ToastContainer position="top-right" autoClose={3000} theme="colored" />
        </WishlistProvider>
      </CartProvider>
    </AuthProvider>
  </StrictMode>,
)