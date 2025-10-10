import React, { useState } from "react";
import logo from "../../assets/Logo.png";

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

        {/* Start / Stop buttons */}
        <div className="col d-flex justify-content-center mt-3">
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

      {/* Location Input */}
      <div
        className="d-flex justify-content-center align-items-center mt-3"
        style={{ gap: 10 }}
      >
        <input
          type="text"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          placeholder="Enter location..."
          className="form-control rounded-pill px-3"
          style={{
            width: "250px",
            backgroundColor: "#f8f9fa",
            border: "1px solid #ccc",
          }}
        />
        <button
          className="btn btn-primary rounded-pill px-4"
          onClick={handleSearch}
        >
          Go
        </button>
      </div>

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
