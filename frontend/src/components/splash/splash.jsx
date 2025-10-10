import React, { useState, useEffect } from "react";
import logo from "../../assets/Logo.png";
import "./Splash.css";

export default function Splash({ onFinish }) {
  const [fadeOut, setFadeOut] = useState(false);

  useEffect(() => {
    // Start fade-out slightly before the total duration
    const fadeTimer = setTimeout(() => setFadeOut(true), 2200); // start fade at 1.2s

    // Finish splash after 1.5 seconds
    const finishTimer = setTimeout(() => onFinish(), 2500);

    return () => {
      clearTimeout(fadeTimer);
      clearTimeout(finishTimer);
    };
  }, [onFinish]);

  return (
    <div className={`splash-container ${fadeOut ? "fade-out" : ""}`}>
      <img src={logo} alt="Logo" className="splash-logo" />
      <h1 className="splash-text">Welcome to UAV Simulation</h1>
    </div>
  );
}
