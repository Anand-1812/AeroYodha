import React from "react";
import logo from "../../assets/Logo.png"

const Controls = ({
  running,
  setRunning,
  stop,
  uavs,
  handleAddUavs,
}) => {
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
