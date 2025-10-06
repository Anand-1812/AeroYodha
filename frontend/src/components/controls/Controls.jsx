import React from "react";

const Controls = ({ 
  running, 
  setRunning, 
  stop, 
  refreshData, 
  uavs, 
  uavCount, 
  setUavCount, 
  handleAddUavs 
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
          <h2>AeroYodha</h2>
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
      <button className="btn-generic rounded-pill" onClick={refreshData}>
        Refresh from API
      </button>

      {/* UAV Count Control */}
      <div style={{ marginTop: "10px" }}>
        <label style={{ marginRight: "10px" }}>Number of UAVs:</label>
        <input
          type="number"
          value={uavCount}
          onChange={(e) => setUavCount(e.target.value)}
          min="1"
          style={{ width: "60px", marginRight: "10px" }}
        />
        <button onClick={handleAddUavs} className="btn-generic rounded-pill">
          Generate UAVs
        </button>
      </div>

      {/* Status */}
      <div className="text-white opacity-75" style={{ marginLeft: "auto" }}>
        <strong>UAVs:</strong> {uavs.length}
      </div>
    </div>
  );
};

export default Controls;
