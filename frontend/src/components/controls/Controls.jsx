import React from "react";

const Controls = ({
  running,
  setRunning,
  stop,
  refreshData,
  uavs,
}) => {
  return (
    <div style={{ padding: 12, borderBottom: "1px solid #ddd", display: "flex", gap: 12, alignItems: "center", flexDirection:"column"}}>
    <div className="row">
        <div className="col">
            <button onClick={() => setRunning((r) => !r)}>start</button>
    <button className="ms-4" onClick={stop}>Stop</button>
        </div>
    
    </div>
      <button onClick={refreshData}>Refresh from API</button>
      <div style={{ marginLeft: "auto" }}>
        <strong>UAVs:</strong> {uavs.length}
      </div>
    </div>
  );
};

export default Controls;
