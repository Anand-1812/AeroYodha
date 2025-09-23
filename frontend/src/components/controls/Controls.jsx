import React from "react";

const Controls = ({ running, setRunning, stop, refreshData, uavs }) => {
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
      <div className="row">
        <div className="col  d-flex justify-content-center">
            <h2>AeroYodha</h2>
        </div>
        <div className="col d-flex justify-content-center mt-3">
          <button className="str-btn rounded-pill" onClick={() => setRunning((r) => !r)}>start</button>
          <button className="end-btn rounded-pill ms-5" onClick={stop}>
            Stop
          </button>
        </div>
      </div>
      <button className="btn-generic rounded-pill" onClick={refreshData}>Refresh from API</button>
      <div className="text-white opacity-75" style={{ marginLeft: "auto" }}>
        <strong>UAVs:</strong> {uavs.length}
      </div>
    </div>
  );
};

export default Controls;
