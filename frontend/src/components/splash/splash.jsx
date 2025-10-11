import React, { useState, useEffect } from "react";
import logo from "../../assets/Logo.png";
import "./Splash.css";

export default function Splash({ onFinish }) {
  const [fadeOut, setFadeOut] = useState(false);

  useEffect(() => {
    const fadeTimer = setTimeout(() => setFadeOut(true), 2000);
    const finishTimer = setTimeout(() => onFinish(), 2000);
    return () => {
      clearTimeout(fadeTimer);
      clearTimeout(finishTimer);
    };
  }, [onFinish]);

  return (
    <div className={`splash-container ${fadeOut ? "fade-out" : ""}`}>
      <img src={logo} style={{height:200, width:550}}alt="Logo" className="splash-logo" />
      <h1 className="splash-text">Welcome to UTM Simulation</h1>

      <div className="splash-footer">
        Made with <span className="heart">❤</span> by <strong>Biplob</strong>, <strong>Anand</strong>, and <strong>Dev</strong>
      </div>
    </div>
  );
}
