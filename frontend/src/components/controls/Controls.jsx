import React, { useState, useEffect } from "react";
import logo from "../../assets/Logo.png";
import "./Controls.css";

const Controls = ({
  running,
  setRunning,
  stop,
  uavs,
  handleAddUavs,
  handleLocationSearch,
}) => {
  const [location, setLocation] = useState("");
  const [elapsedTime, setElapsedTime] = useState(0);
  const [sessions, setSessions] = useState(0);

  // Timer logic
  useEffect(() => {
    let timer;
    if (running) {
      timer = setInterval(() => {
        setElapsedTime((prev) => prev + 1);
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [running]);

  // Handle session increment when simulation starts
  useEffect(() => {
    if (running) {
      setSessions((prev) => prev + 1);
    }
  }, [running]);

  const handleSearch = () => {
    if (handleLocationSearch && location.trim() !== "") {
      handleLocationSearch(location.trim());
      setLocation("");
    }
  };

  // Format elapsed time (hh:mm:ss)
  const formatTime = (seconds) => {
    const h = Math.floor(seconds / 3600)
      .toString()
      .padStart(2, "0");
    const m = Math.floor((seconds % 3600) / 60)
      .toString()
      .padStart(2, "0");
    const s = (seconds % 60).toString().padStart(2, "0");
    return `${h}:${m}:${s}`;
  };

  return (
    <div
      style={{
        padding: 12,
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
            <button
              className="end-btn rounded-pill ms-5"
              onClick={() => {
                stop();
                setElapsedTime(0);
              }}
            >
              Stop
            </button>
          </div>
        </div>
      </div>

      {/* Refresh */}
      <button
        className="refresh mt-2"
        onClick={() => window.location.reload()}
      >
        Refresh Site
      </button>

      {/* Status Section */}
      <div
        className="text-white opacity-75"
        style={{
          display: "flex",
          justifyContent: "space-between",
          width: "100%",
          maxWidth: 300,
          marginTop: 10,
        }}
      >
        <div>
          <strong>UAVs:</strong> {uavs.length}
        </div>
        <div>
          <strong>Sessions:</strong> {sessions}
        </div>
      </div>

      {/* Timer Display */}
      <div className="text-white timebox opacity-75">
        {/* your content here */}⏱ Time Elapsed: {formatTime(elapsedTime)}
      </div>
    </div>
  );
};

export default Controls;
