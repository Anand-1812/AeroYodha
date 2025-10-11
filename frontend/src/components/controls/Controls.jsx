import React, { useState } from "react";
import logo from "../../assets/Logo.png";
import "./Controls.css";

const Controls = ({
  running,
  setRunning,
  stop,
  uavs,
  handleAddUavs,
  handleLocationSearch, // <-- optional callback for map integration
}) => {
  const [location, setLocation] = useState("");

  const handleSearch = () => {
    if (handleLocationSearch && location.trim() !== "") {
      handleLocationSearch(location.trim());
      setLocation("");
    }
  };

  return (
    <div
      style={{
        padding: 12,
        borderBottom: "1px solid #ddd",
        display: "flex",
        gap: 12,
        alignItems: "center",
        flexDirection: "column",
      }}
    >
      {/* Title */}
      <div className="row">
        <div className="col d-flex justify-content-center">
          <img src={logo} alt="Logo" style={{ height: 100, width: 300 }} />
        </div>

        <div
          className="d-flex justify-content-center align-items-center mt-3"
          style={{ gap: 10 }}
        >
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="Enter state or city"
            className="controls-input"
          />
          <button
            className="btn btn-primary rounded-pill controls-btn go px-4 py-2"
            onClick={handleSearch}
          >
            Go
          </button>
        </div>
        <div className="upperbox">
          <div className="col d-flex justify-content-center mt-3 pb-2">
            <button
              className="str-btn rounded-pill"
              onClick={() => setRunning((r) => !r)}
            >
              {running ? "Pause" : "Start"}
            </button>
            <button className="end-btn rounded-pill ms-5" onClick={stop}>
              Stop
            </button>
          </div>
        </div>
      </div>

      {/* Location Input */}

      {/* Refresh */}
      <button
        className="btn-generic rounded-pill mt-2"
        onClick={() => window.location.reload()}
      >
        Refresh Site
      </button>

      {/* Status */}
      <div className="text-white opacity-75" style={{ marginLeft: "auto" }}>
        <strong>UAVs:</strong> {uavs.length}
      </div>
    </div>
  );
};

export default Controls;
