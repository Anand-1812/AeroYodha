import React from "react";
import logo from "../../assets/Logo.png"

const Controls = ({
  running,
  setRunning,
  stop,
  refreshData,
  uavs,
  uavCount,
  setUavCount,
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
          {/* <h2>AeroYodha</h2> */}
          <img src={logo} alt="Logo" style={{height:100 , width:300}}></img>
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
        <div className="input-group mb-3" style={{ width: "120px" }}>
          <span className="input-group-text bg-dark text-white border-dark" id="uav-count-addon">
            UAVs:
          </span>
          <input
            type="number"
            className="form-control bg-dark text-white border-dark"
            value={uavCount}
            onChange={(e) => setUavCount(e.target.value)}
            min="1"
            max="8"
            aria-label="Number of UAVs"
            aria-describedby="uav-count-addon"
          />
        </div>
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
