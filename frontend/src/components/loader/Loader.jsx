import React, { useMemo } from "react";

export default function Loader() {
    const particles = useMemo(() => {
        return Array.from({ length: 24 }, (_, i) => ({
            id: i,
            size: Math.random() * 14 + 6,
            left: Math.random() * 100,
            top: Math.random() * 100,
            duration: 6 + Math.random() * 8,
            delay: Math.random() * 5,
            blue: Math.random() > 0.72,
        }));
    }, []);

  return (
    <>
        <div className="loader-page">
            <div className="particles">
                {particles.map((particle) => (
                    <span key={particle.id} className={`particle ${particle.gold ? "pink" : ""}`} style={{
                        width: `${particle.size}px`,
                        height: `${particle.size}px`,
                        left: `${particle.left}%`,
                        top: `${particle.top}%`,
                        animationDuration: `${particle.duration}s`,
                        animationDelay: `${particle.delay}s`,
                    }} />
                ))}
            </div>

            <div className="loader-core">
                <div className="center-dot"></div>
                <div className="center-text">LOADING</div>

                <svg viewBox="0 0 200 200" aria-hidden="true">
                    <circle className="ring outer" cx="100" cy="100" r="78" strokeDasharray="90 60 30 40 70 120" />
                    <circle className="ring mid" cx="100" cy="100" r="60" strokeDasharray="70 30 40 60 25 50" transform="rotate(25 100 100)" />
                    <circle className="ring inner" cx="100" cy="100" r="42" strokeDasharray="40 25 30 20 35 45" transform="rotate(-20 100 100)" />
                    <circle className="ring small"cx="100" cy="100" r="24" strokeDasharray="20 16 14 10 18 30" transform="rotate(35 100 100)" />
                </svg>
            </div>
        </div>      
    </>
  );
}