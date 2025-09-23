import React from "react";

const Controls = ({
  running,
  setRunning,
  stop,
  refreshData,
  uavs,
}) => {
  return (
    <div style={{ padding: 12, borderBottom: "1px solid #ddd", display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
      <button onClick={() => setRunning((r) => !r)}>{running ? "Pause" : "Start"}</button>
      <button onClick={stop}>Stop</button>
      <button onClick={refreshData}>Refresh from API</button>

      <div style={{ marginLeft: "auto" }}>
        <strong>UAVs:</strong> {uavs.length}
      </div>
    </div>
  );
};

export default Controls;
