import React, { useEffect, useState, useRef } from "react";
import { useLocation, useNavigate, Link } from "react-router-dom";

import logo from '../../assets/image/logo/vastrika-logo.png';
import useNavToggle from "../../hooks/useNavToggle"; // canvas menu
import { useVoiceSearch } from "../../hooks/voiceSearch/VoiceSearch"; // Voice search (Web Speech API)
import { useSearchApi } from "../../hooks/voiceSearch/useSearchApi";
import { useCart } from "../../context/CartContext";
import { useAuth } from "../../context/AuthContext";
import { toast } from "react-toastify";
import { megaMenuData } from "../../data/megaMenuData";

const PRODUCTS_API =
    import.meta.env.VITE_PRODUCTS_API || "http://127.0.0.1:8000/api/products";

const Header = () => {
    // if (!menu || !isOpen) return null;

    const navigate = useNavigate();
    const { user, isLoggedIn, logout } = useAuth();
    const { cartCount, wishlistCount } = useCart(); // dynamic cart and whislist count
    const { toggleNav, closeNav } = useNavToggle(); // canvas menu

    const [query, setQuery] = useState(""); // Voice search (Web Speech API)
    const [debouncedQuery, setDebouncedQuery] = useState("");
    const [activeMenu, setActiveMenu] = useState(null);
    const [megaMenu, setMegaMenu] = useState([]);
    const [menuLoading, setMenuLoading] = useState(true);
    const location = useLocation();

    useEffect(() => {
        const fetchMegaMenu = async () => {
            try {
                const res = await fetch(`${PRODUCTS_API}/menu/`);

                if (!res.ok) {
                    throw new Error("Failed to load mega menu");
                }

                const data = await res.json();
                setMegaMenu(Array.isArray(data) ? data : []);
            } catch (error) {
                console.error("Mega menu error:", error);
                setMegaMenu([]);
            } finally {
                setMenuLoading(false);
            }
        };

        fetchMegaMenu();
    }, []);

    useEffect(() => {
        const delay = setTimeout(() => {
            setDebouncedQuery(query);
        }, 400);

        return () => clearTimeout(delay);
    }, [query]);
    const { results, loading, error } = useSearchApi(debouncedQuery);

    const { startVoice, isListening } = useVoiceSearch((text) => {
        setQuery(text); // voice → input → API
    });

    const headerRef = useRef(null);

    // Logout handler
    const handleLogout = async () => {
        const result = await logout();

        if (!result?.success) {
            toast.error(result?.message || "Logout failed");
            return;
        }

        toast.success(result?.message || "Logout successful");

        navigate("/");
    };

    // Sticky header
    useEffect(() => {
        // const header = document.querySelector(".menu-sticky");
        // const sections = document.querySelectorAll("section");
        // const rsHeader = document.getElementById("rs-header");

        const handleScroll = () => {
            // Sticky Menu
            if (!headerRef.current) return;

            // const scroll = window.scrollY;
            if (window.scrollY > 0) {
                headerRef.current.classList.add("sticky");
            } else {
                headerRef.current.classList.remove("sticky");
            }
        };

        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    return (
        <>
            {/* Full width header Start */}
            <div className="full-width-header header-style2">
                
                {/* Toolbar Start */}
                <div className="toolbar-area hidden-md">
                    <div className="container">
                        <div className="row">
                            <div className="col-md-5">
                                <div className="toolbar-contact">
                                    <ul>
                                        <li>
                                            <i className="fa fa-envelope" style={{ color: "white" }}></i>&nbsp;&nbsp;
                                            <a href="mailto:support@example.com">support@example.com</a>
                                        </li>
                                        <li>
                                            <i className="fa fa-phone" style={{ color: "white", fontSize: "19px" }}></i>&nbsp;&nbsp;
                                            <a href="tel:+911234567890">+91-1234567890</a>
                                        </li>
                                    </ul>
                                </div>
                            </div>

                            <div className="col-md-7">
                                <div className="toolbar-sl-share">
                                    <ul>
                                        <li>
                                            <a href="https://www.instagram.com" target="_blank" rel="noopener noreferrer">
                                                <i className="fa fa-instagram"></i>
                                            </a>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                {/* Toolbar End */}

                {/* Header Start */}
                <header id="rs-header" className="rs-header">

                    {/* Menu Start */}
                    <div className="menu-area menu-sticky" ref={headerRef}>
                        <div className="container">
                            <div className="row">

                                {/* Logo */}
                                <div className="col-lg-3">
                                    <div className="logo-area">
                                        <Link to="/" className="dark"><img src={logo} alt="Vastrika Logo" /></Link>
                                        <Link to="/" className="light"><img src={logo} alt="Vastrika Logo" /></Link>
                                    </div>
                                </div>
                                {/* end-logo  */}

                                {/* Right Side */}
                                <div className="col-lg-9 text-right">
                                    <div className="rs-menu-area">
                                        <div className="main-menu">
                                            <div className="mobile-menu">
                                                <a className="rs-menu-toggle" aria-label="Toggle menu">
                                                    <i className="fa fa-bars"></i>
                                                </a>
                                            </div>

                                            {/* nav-menu start */}
                                            <nav className="rs-menu pr-65">
                                                <ul className="nav-menu">
                                                    {megaMenuData.map((menu) => {
                                                        const isActive =
                                                         location.pathname === "/" && menu.slug === "men" ? true : location.pathname.startsWith(`/products/${menu.slug}`);

                                                        return (
                                                            <li  key={`menu-${menu.slug}`} className={`rs-mega-menu mega-rs dropdown ${
                                                                isActive ? "current-menu-item" : ""}`}
                                                                onMouseEnter={() => setActiveMenu(menu.slug)}
                                                                onMouseLeave={() => setActiveMenu(null)}>
                                                                <Link to={`/products/${menu.slug}`} className={`nav-link ${isActive ? "active-link" : ""}`}>{menu.label}</Link>

                                                                {activeMenu === menu.slug && menu.sections?.length > 0 && (
                                                                    <div className="mega-box">
                                                                        <div className="content">
                                                                            {menu.sections.map((section) => (
                                                                                <div className="rows" key={`section-${menu.slug}-${section.slug}`}>
                                                                                    <p>
                                                                                        <Link to={`/products/${menu.slug}/${section.slug}`}>
                                                                                            {section.label}
                                                                                        </Link>
                                                                                    </p>

                                                                                    {/* <p>Topwear</p> */}
                                                                                    <ul className="mega-links">
                                                                                        {section.items?.map((item) => (
                                                                                            <li key={`item-${menu.slug}-${section.slug}-${item.slug}`}>
                                                                                                <Link to={`/products/${menu.slug}/${section.slug}/${item.slug}`}>
                                                                                                    {item.label}
                                                                                                </Link>
                                                                                            </li>
                                                                                            // <li><Link to="/">T-shirts</Link></li>
                                                                                            // <li><Link to="/">Casual shirts</Link></li>
                                                                                            // <li><Link to="/">Formal shirts</Link></li>
                                                                                            // <li><Link to="/">Jackets</Link></li>
                                                                                            // <li><Link to="/">Blazers & Coats</Link></li>
                                                                                        ))}
                                                                                    </ul>
                                                                                </div>
                                                                            ))}
                                                                            {/* <div className="rows">
                                                                                <p>Bottomwear</p>
                                                                                <ul className="mega-links">
                                                                                    <li><Link to="/">Jeans</Link></li>
                                                                                    <li><Link to="/">Casual Trousers</Link></li>
                                                                                    <li><Link to="/">Formal Trousers</Link></li>
                                                                                    <li><Link to="/">Shorts</Link></li>
                                                                                    <li><Link to="/">Track Pants & Joggers</Link></li>
                                                                                </ul>
                                                                            </div> */}
                                                                            {/* <div className="rows">
                                                                                <p>Innerwear & Sleepwear</p>
                                                                                <ul className="mega-links">
                                                                                    <li><Link to="/">Briefs & Trunks</Link></li>
                                                                                    <li><Link to="/">Boxers</Link></li>
                                                                                    <li><Link to="/">Vests</Link></li>
                                                                                    <li><Link to="/">Sleepwear & Loungewear</Link></li>
                                                                                    <li><Link to="/">Thermals</Link></li>
                                                                                </ul>
                                                                            </div> */}
                                                                            {/* <div className="rows">
                                                                                <p>Indian & Festive Wear</p>
                                                                                <ul className="mega-links">
                                                                                    <li><Link to="/">Kurtas & Kurta Sets</Link></li>
                                                                                    <li><Link to="/">Sherwanis</Link></li>
                                                                                    <li><Link to="/">Nehru Jackets</Link></li>
                                                                                    <li><Link to="/">Dhotis</Link></li>
                                                                                </ul>
                                                                            </div> */}
                                                                            {/* <div className="rows">
                                                                                <p>Footwear</p>
                                                                                <ul className="mega-links">
                                                                                    <li><Link to="/">Casual Shoes</Link></li>
                                                                                    <li><Link to="/">Sports Shoes</Link></li>
                                                                                    <li><Link to="/">Formal Shoes</Link></li>
                                                                                    <li><Link to="/">Socks</Link></li>
                                                                                </ul>
                                                                            </div> */}
                                                                        </div>
                                                                    </div>
                                                                )}
                                                            </li>
                                                        );
                                                    })}

                                                    {/* <li className="rs-mega-menu mega-rs dropdown"><Link to="/" onClick={(e) => e.preventDefault()}>Women</Link>
                                                        <div className="mega-box">
                                                            <div className="content">
                                                                <div className="rows">
                                                                    <p>Indian Wear</p>
                                                                    <ul className="mega-links">
                                                                        <li><Link to="/">Kurtas & Suits</Link></li>
                                                                        <li><Link to="/">Kurtis, Tunics & Tops</Link></li>
                                                                        <li><Link to="/">Sarees</Link></li>
                                                                        <li><Link to="/">Ethnic Wear</Link></li>
                                                                        <li><Link to="/">Salwars & Churidars</Link></li>
                                                                        <li><Link to="/">Lehenga Cholis</Link></li>
                                                                        <li><Link to="/">Dupattas & Shawls</Link></li>
                                                                        <li><Link to="/">Jackets</Link></li>
                                                                    </ul>
                                                                </div>
                                                                <div className="rows">
                                                                    <p>Western Wear</p>
                                                                    <ul className="mega-links">
                                                                        <li><Link to="/">Tops & Tshirts</Link></li>
                                                                        <li><Link to="/">Jackets & Coats</Link></li>
                                                                        <li><Link to="/">Blazers & Waistcoats</Link></li>
                                                                    </ul>
                                                                </div>
                                                                <div className="rows">
                                                                    <p>BottomWear</p>
                                                                    <ul className="mega-links">
                                                                        <li><Link to="/">Skirts & Palazzos</Link></li>
                                                                        <li><Link to="/">Jeans & Trousers</Link></li>
                                                                        <li><Link to="/">Shorts & Co-ords</Link></li>
                                                                        <li><Link to="/">Playsuits & Jumpsuits</Link></li>
                                                                    </ul>
                                                                </div>
                                                                <div className="rows">
                                                                    <p>Lingerie & Sleepwear</p>
                                                                    <ul className="mega-links">
                                                                        <li><Link to="/">Bra & Briefs</Link></li>
                                                                        <li><Link to="/">Sleepwear & Loungewear</Link></li>
                                                                        <li><Link to="/">Swimwear</Link></li>
                                                                        <li><Link to="/">Camisoles & Thermals</Link></li>
                                                                    </ul>
                                                                </div>
                                                                <div className="rows">
                                                                    <p>Footwear</p>
                                                                    <ul className="mega-links">
                                                                        <li><Link to="/">Casual Shoes</Link></li>
                                                                        <li><Link to="/">Heels & Boots</Link></li>
                                                                        <li><Link to="/">Sports Shoes & Floaters</Link></li>
                                                                    </ul>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </li> */}

                                                    {/* <li className="rs-mega-menu mega-rs"><Link to="/" onClick={(e) => e.preventDefault()}>Kids</Link>
                                                        <div className="mega-box">
                                                            <div className="content">
                                                                <div className="rows">
                                                                    <p>Boys Clothing</p>
                                                                    <ul className="mega-links">
                                                                        <li><Link to="/">T-Shirts & Shirts</Link></li>
                                                                        <li><Link to="/">Shorts & Jeans</Link></li>
                                                                        <li><Link to="/">Trousers</Link></li>
                                                                        <li><Link to="/">Track Pants & Pyjamas</Link></li>
                                                                    </ul>
                                                                </div>
                                                                <div className="rows">
                                                                    <p>Girls Clothing</p>
                                                                    <ul className="mega-links">
                                                                        <li><Link to="/">Tops & Tshirts</Link></li>
                                                                        <li><Link to="/">Lehenga choli & Kurta Sets</Link></li>
                                                                        <li><Link to="/">Dungarees & Jumpsuits</Link></li>
                                                                        <li><Link to="/">Tights & Leggings</Link></li>
                                                                        <li><Link to="/">Jeans, Trousers & Capris</Link></li>
                                                                    </ul>
                                                                </div>
                                                                <div className="rows">
                                                                    <p>Infants</p>
                                                                    <ul className="mega-links">
                                                                        <li><Link to="/">Bodysuits</Link></li>
                                                                        <li><Link to="/">Rompers & Sleepsuits</Link></li>
                                                                        <li><Link to="/">Tshirts & Tops</Link></li>
                                                                        <li><Link to="/">Bottom wear</Link></li>
                                                                        <li><Link to="/">Innerwear & Sleepwear</Link></li>
                                                                    </ul>
                                                                </div>
                                                                <div className="rows">
                                                                    <p>Footwear</p>
                                                                    <ul className="mega-links">
                                                                        <li><Link to="/">Casual Shoes</Link></li>
                                                                        <li><Link to="/">Sports Shoes</Link></li>
                                                                        <li><Link to="/">Sandals & Heels</Link></li>
                                                                        <li><Link to="/">School Shoes & Socks</Link></li>
                                                                    </ul>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </li> */}
                                                    {/* <li className="rs-mega-menu mega-rs"><Link to="/" onClick={(e) => e.preventDefault()}>Beauty</Link>
                                                        <div className="mega-box">
                                                            <div className="content">
                                                                <div className="rows">
                                                                    <p>Makeup</p>
                                                                    <ul className="mega-links">
                                                                        <li><Link to="/">Lipstick & Lip Gloss</Link></li>
                                                                        <li><Link to="/">Lip Liner & Eyeliner</Link></li>
                                                                        <li><Link to="/">Mascara & Kajal</Link></li>
                                                                        <li><Link to="/">Eyeshadow & Foundation</Link></li>
                                                                        <li><Link to="/">Primer & Concealer</Link></li>
                                                                        <li><Link to="/">Compact & Nail Polish</Link></li>
                                                                    </ul>
                                                                </div>
                                                                <div className="rows">
                                                                    <p>Skincare, Bath & Body</p>
                                                                    <ul className="mega-links">
                                                                        <li><Link to="/">Face Moisturiser</Link></li>
                                                                        <li><Link to="/">Masks & Peel</Link></li>
                                                                        <li><Link to="/">Sunscreen & Serum</Link></li>
                                                                        <li><Link to="/">Face Wash & Cleanser</Link></li>
                                                                        <li><Link to="/">Eye Cream & Lip Balm</Link></li>
                                                                        <li><Link to="/">Body Lotion & Body Wash</Link></li>
                                                                        <li><Link to="/">Body Scrub & Hand Cream</Link></li>
                                                                    </ul>
                                                                </div>
                                                                <div className="rows">
                                                                    <p>Haircare</p>
                                                                    <ul className="mega-links">
                                                                        <li><Link to="/">Shampoo & Conditioner</Link></li>
                                                                        <li><Link to="/">Hair Cream & Hair Oil</Link></li>
                                                                        <li><Link to="/">Hair Gel & Hair Color</Link></li>
                                                                        <li><Link to="/">Hair Serum</Link></li>
                                                                    </ul>
                                                                </div>
                                                                <div className="rows">
                                                                    <p>Fragrances</p>
                                                                    <ul className="mega-links">
                                                                        <li><Link to="/">Perfume</Link></li>
                                                                        <li><Link to="/">Deodorant</Link></li>
                                                                        <li><Link to="/">Body Mist</Link></li>
                                                                    </ul>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </li> */}
                                                    {/* <li className="rs-mega-menu mega-rs"><Link to="/" onClick={(e) => e.preventDefault()}>Accessories</Link>
                                                        <div className="mega-box">
                                                            <div className="content">
                                                                <div className="rows">
                                                                    <p>Men Accessories</p>
                                                                    <ul className="mega-links">
                                                                        <li><Link to="/">Watches</Link></li>
                                                                        <li><Link to="/">Belts & Wallets</Link></li>
                                                                        <li><Link to="/">Caps & Hats</Link></li>
                                                                        <li><Link to="/">Sports Accessories</Link></li>
                                                                        <li><Link to="/">Sunglasses</Link></li>
                                                                    </ul>
                                                                </div>
                                                                <div className="rows">
                                                                    <p>Women Accessory</p>
                                                                    <ul className="mega-links">
                                                                        <li><Link to="/">Watches</Link></li>
                                                                        <li><Link to="/">Sunglasses</Link></li>
                                                                        <li><Link to="/">Hair Accessories</Link></li>
                                                                        <li><Link to="/">Sports Accessories</Link></li>
                                                                        <li><Link to="/">Scarves and Stoles</Link></li>
                                                                    </ul>
                                                                </div>
                                                                <div className="rows">
                                                                    <p>Kids Accessories</p>
                                                                    <ul className="mega-links">
                                                                        <li><Link to="/">Toys & Games</Link></li>
                                                                        <li><Link to="/">Bags & Backpacks</Link></li>
                                                                        <li><Link to="/">Watches</Link></li>
                                                                        <li><Link to="/">Jewellery & Hair accessory</Link></li>
                                                                        <li><Link to="/">Sunglasses</Link></li>
                                                                        <li><Link to="/">Masks & Protective Gears</Link></li>
                                                                        <li><Link to="/">Caps & Hats</Link></li>
                                                                    </ul>
                                                                </div>
                                                                <div className="rows">
                                                                    <p>Bathroom Accessories</p>
                                                                    <ul className="mega-links">
                                                                        <li><Link to="/">Bath Towels</Link></li>
                                                                        <li><Link to="/">Hand & Face Towels</Link></li>
                                                                        <li><Link to="/">Beach Towels</Link></li>
                                                                        <li><Link to="/">Towels Set</Link></li>
                                                                    </ul>
                                                                </div>
                                                                <div className="rows">
                                                                    <p>Home Accessories</p>
                                                                    <ul className="mega-links">
                                                                        <li><Link to="/">Bed Linen & Furnishing</Link></li>
                                                                        <li><Link to="/">Flooring</Link></li>
                                                                        <li><Link to="/">Lamps & Lighting</Link></li>
                                                                        <li><Link to="/">Kitchen & Table</Link></li>
                                                                        <li><Link to="/">Cushions & Cushion Covers</Link></li>
                                                                        <li><Link to="/">Storage</Link></li>
                                                                    </ul>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </li> */}
                                                </ul>
                                            </nav>
                                            {/* end-of-nav-menu */}
                                        </div>

                                        {/* //.main-menu */}
                                        <div className="expand-btn-inner">
                                            <ul>
                                                {/* Search */}
                                                <li className="search-bar">
                                                    <input type="text" id="searchInput" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search products..." aria-label="Search products" />

                                                    <div className="mic" onClick={startVoice} aria-label="Voice search">
                                                        <i className="material-icons">
                                                            {isListening ? "mic" : "mic_none"}
                                                        </i>
                                                        <div className="mic-shadow"></div>

                                                        {query.trim().length > 1 && (
                                                            <div className="suggestions" id="suggestions">

                                                                {loading ? (
                                                                    <div>Loading...</div>
                                                                ) : error ? (
                                                                    <div>Error: {error}</div>
                                                                ) : results.length > 0 ? (
                                                                    results.map((item, index) => (
                                                                        <div key={`search-${item.id ?? item.name ?? index}`} onClick={() => navigate(`/product/${item.id}`)} style={{ cursor: "pointer" }}>
                                                                            {item.name || item}
                                                                        </div>
                                                                    ))
                                                                ) : (
                                                                    <div>No results found</div>
                                                                )}
                                                            </div>
                                                        )}
                                                    </div>
                                                </li>
                                                {/*end-of-search-bar  */}

                                                {/* hamburger-menu */}
                                                <li>
                                                    <a id="nav-expander" className="humburger nav-expander" href="/" onClick={(e) => {e.preventDefault(); toggleNav();}} aria-label="Open menu">
                                                        <span className="dot1"></span>
                                                        <span className="dot2"></span>
                                                        <span className="dot3"></span>
                                                        <span className="dot4"></span>
                                                        <span className="dot5"></span>
                                                        <span className="dot6"></span>
                                                        <span className="dot7"></span>
                                                        <span className="dot8"></span>
                                                        <span className="dot9"></span>
                                                    </a>
                                                </li>
                                                {/* end-hamburger-menu */}
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    {/* Menu End */}

                    {/* Canvas Menu start */}
                    <nav className="right_menu_togle hidden-md">
                        <div className="close-btn">
                            <span id="nav-close" className="humburger" onClick={closeNav} aria-label="Close menu">
                                <span className="dot1"></span>
                                <span className="dot2"></span>
                                <span className="dot3"></span>
                                <span className="dot4"></span>
                                <span className="dot5"></span>
                                <span className="dot6"></span>
                                <span className="dot7"></span>
                                <span className="dot8"></span>
                                <span className="dot9"></span>
                            </span>
                        </div>
                        {/* bottom-navigation */}
                        <div className="bottom-nav">

                            {/*  */}
                            <div className="profile-wrapper">
                                {/* profile icon */}
                                <div className="profile-trigger">
                                    <span className="active"><i className="fa fa-user" style={{ fontSize: "22px" }}></i></span>
                                    <span className="label">Profile</span>
                                </div>

                                {/* Dropdown */}
                                <div className="profile-dropdown">
                                    <div className="profile-header">
                                        <p>To access account and manage orders</p>
                                        <div className="login__system">
                                            {!isLoggedIn ? (
                                                <>
                                                    <button className="login-btn" onClick={() => navigate("/login")}>Login / Signup</button>
                                                </>
                                            ) : (
                                                // when logged in
                                                <>
                                                    <p style={{fontWeight:"600"}}>Hello, {user?.first_name}</p>
                                                    <button className="login-btn" style={{fontSize:"16px"}} onClick={handleLogout}>Logout</button>
                                                </>
                                            )}
                                        </div>
                                    </div>

                                    <hr />
                                    <ul className="menu-list">
                                        <li><Link to={'/my-account'} className="drop-menu">Your Account</Link></li>
                                        <li><Link to="#" className="drop-menu">Your Orders</Link></li>
                                        <li><Link to="#" className="drop-menu">Contact Us</Link></li>
                                        <li><Link to="#" className="drop-menu">Your Seller Account</Link></li>
                                    </ul>
                                </div>
                            </div>                    
                            {/*  */}

                            <Link to={'/wishlist'}><i className="fa fa-heart"></i>
                                {wishlistCount > 0 && (
                                    <span className="count" style={{ marginLeft: "30px" }}>{wishlistCount}</span>
                                )}
                                <p>Wishlist</p>
                            </Link>
                            <Link to={'/cart'}><i className="fa fa-shopping-bag"></i>
                                {cartCount > 0 && (
                                    <span className="count" style={{ marginLeft: "13px" }}>{cartCount}</span>
                                )}
                                <p>Bag</p>
                            </Link>
                        </div>
                        <div className="canvas-contact">
                            <ul className="contact">
                                <li><i className="fa fa-map-marker" style={{ fontSize: "22px" }}></i>&nbsp;&nbsp;<a href="/" onClick={(e) => e.preventDefault()}>Contai, Purba Medinipur West Bengal - 721401</a></li>
                                <li><i className="fa fa-phone" style={{ fontSize: "22px" }}></i>&nbsp;&nbsp;<a href="tel:+91-1234567890">+91-1234567890</a></li>
                                <li><i className="fa fa-envelope" style={{ fontSize: "18px" }}></i>&nbsp;&nbsp;<a href="mailto:support@example.com">support@example.com</a></li>
                            </ul>
                            <ul className="social">
                                <li><a href="https://www.instagram.com" target="_blank" rel="noopener noreferrer"><i className="fa fa-instagram"></i></a></li>
                            </ul>
                        </div>
                    </nav>
                    {/* Canvas Menu end */}

                </header>
                {/* Header End */}
            </div>
            {/* Full width header End */}
        </>
    );
};

export default Header;