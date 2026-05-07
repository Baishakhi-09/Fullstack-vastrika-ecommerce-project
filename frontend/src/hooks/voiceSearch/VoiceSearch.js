import { useRef, useState, useEffect } from "react";

export function useVoiceSearch(onResult) {
    const recognitionRef = useRef(null);
    const [isListening, setIsListening] = useState(false);
    const [error, setError] = useState(null);

    // ------------------ INIT ------------------ //
    const getRecognition = () => {
        const SpeechRecognition =
            window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            setError("Voice search not supported in this browser");
            return null;
        }

        const recognition = new SpeechRecognition();
        recognition.lang = "en-IN";
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        return recognition;
    };

    // ------------------ START ------------------ //
    const startVoice = () => {
        const recognition = getRecognition();
        if (!recognition) return;

        recognitionRef.current = recognition;

        recognition.onstart = () => {
            setIsListening(true);
            setError(null);
        };

        recognition.onresult = (e) => {
            const text = e.results?.[0]?.[0]?.transcript || "";
            if (text) onResult(text);
        };

        recognition.onerror = (e) => {
            console.error("Voice error:", e.error);
            setError(e.error);
            setIsListening(false);
        };

        recognition.onend = () => {
            setIsListening(false);
        };

        recognition.start();
    };

    // ------------------ STOP ------------------ //
    const stopVoice = () => {
        if (recognitionRef.current) {
            recognitionRef.current.stop();
            setIsListening(false);
        }
    };

    // ------------------ CLEANUP ------------------ //
    useEffect(() => {
        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.stop();
            }
        };
    }, []);

    return { startVoice, stopVoice, isListening, error, };
}