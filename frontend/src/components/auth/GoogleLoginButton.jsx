import { useEffect, useRef } from "react";
import { toast } from "react-toastify";
import { useAuth } from "../../context/AuthContext";

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

export default function GoogleLoginButton() {
    const buttonRef = useRef(null);
    const initializedRef = useRef(false);
    const { googleLogin } = useAuth();

    useEffect(() => {
        let timeoutId;

        const renderGoogleButton = () => {
            if (initializedRef.current) return;
            if (!buttonRef.current) return;

            if (!GOOGLE_CLIENT_ID) {
                return;
            }

            if (!window.google?.accounts?.id) {
                timeoutId = setTimeout(renderGoogleButton, 300);
                return;
            }

            initializedRef.current = true;

            window.google.accounts.id.initialize({
                client_id: GOOGLE_CLIENT_ID,
                callback: async (response) => {
                    const result = await googleLogin(response.credential);

                    if (!result.success) {
                        toast.error(result.message || "Google login failed");
                        return;
                    }

                    toast.success(result.message || "Google login successful");
                    window.location.href = "/";
                },
            });

            buttonRef.current.innerHTML = "";

            window.google.accounts.id.renderButton(buttonRef.current, {
                theme: "outline",
                size: "large",
                text: "continue_with",
                shape: "rectangular",
                width: 195,
            });
        };

        renderGoogleButton();

        return () => {
            if (timeoutId) clearTimeout(timeoutId);
        };
    }, [googleLogin]);

    return <div ref={buttonRef}></div>;
}