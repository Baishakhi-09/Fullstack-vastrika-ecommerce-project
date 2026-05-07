// Canvas Menu
import { useEffect, useState, useCallback } from "react";

const useNavToggle = () => {
    const [isNavOpen, setIsNavOpen] = useState(false);

    // Open / Close / Toggle (stable functions)
    const openNav = useCallback(() => setIsNavOpen(true), []);
    const closeNav = useCallback(() => setIsNavOpen(false), []);
    const toggleNav = useCallback(() => setIsNavOpen(prev => !prev), []);

    useEffect(() => {
        const body = document.body;

        if (isNavOpen) {
            body.classList.add("nav-expanded");
            body.style.overflow = "hidden"; // prevent scroll
        } else {
            body.classList.remove("nav-expanded");
            body.style.overflow = "";
        }

        // ESC key support
        const handleEsc = (e) => {
            if (e.key === "Escape") {
                closeNav();
            }
        };

        window.addEventListener("keydown", handleEsc);

        return () => {
            window.removeEventListener("keydown", handleEsc);
            body.classList.remove("nav-expanded");
            body.style.overflow = "";
        };

    }, [isNavOpen, closeNav]);

    return {
        isNavOpen,   // expose state (important for UI control)
        openNav,
        closeNav,
        toggleNav,
    };
};

export default useNavToggle;