import { useEffect } from "react";
import { Outlet } from "react-router-dom";

// Global CSS (custom-css)
import "./assets/css/style.css";

// Layout Components
import Header from "./components/header/Header";
import Footer from "./components/footer/Footer";

// Toast Notification
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import Loader from "./components/loader/Loader";

function App() {

  return (
    <>
      <Header />
      <Outlet />
      <Footer />
      <ToastContainer position="top-right" autoClose={3000} theme="colored" />
      <Loader />
    </>
  );
}

export default App;