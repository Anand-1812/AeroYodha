import React, { useState, useEffect } from "react";
import Controls from "./controls/Controls";
import BasicMap from "./map/UAVMap";

export default function UAVSimulation() {
  const [running, setRunning] = useState(false);
  const [uavs, setUavs] = useState([]);
  const [uavCount, setUavCount] = useState(0);
  const [noFlyZones, setNoFlyZones] = useState([]);

  // Mock data (you can replace this with API fetch later)
  const data = {
    ok: true,
    total: 1,
    page: 1,
    limit: 100,
    docs: [
      {
        _id: "68e7d69d5b36908734b74f8e",
        step: 5,
        noFlyZones: [
          [3, 14],
          [7, 8],
          [10, 10],
          [20, 5],
          [25, 17],
        ],
        uavs: [
          {
            id: 0,
            x: 3,
            y: 7,
            start: [0, 0],
            goal: [25, 25],
            reached: false,
            path: [
              [0, 0],
              [1, 1],
              [2, 3],
              [3, 5],
              [3, 7],
            ],
          },
          {
            id: 1,
            x: 12,
            y: 8,
            start: [10, 4],
            goal: [27, 19],
            reached: false,
            path: [
              [10, 4],
              [11, 5],
              [12, 6],
              [12, 8],
            ],
          },
          {
            id: 2,
            x: 8,
            y: 15,
            start: [4, 9],
            goal: [29, 27],
            reached: false,
            path: [
              [4, 9],
              [5, 10],
              [6, 12],
              [7, 14],
              [8, 15],
            ],
          },
          {
            id: 3,
            x: 15,
            y: 20,
            start: [6, 6],
            goal: [28, 28],
            reached: false,
            path: [
              [6, 6],
              [8, 10],
              [10, 14],
              [13, 17],
              [15, 20],
            ],
          },
          {
            id: 4,
            x: 22,
            y: 11,
            start: [12, 7],
            goal: [28, 4],
            reached: false,
            path: [
              [12, 7],
              [14, 8],
              [17, 9],
              [20, 10],
              [22, 11],
            ],
          },
        ],
      },
    ],
  };

  // Load data from JSON
  useEffect(() => {
    const snapshot = data.docs[0];
    setNoFlyZones(snapshot.noFlyZones);
    setUavs(snapshot.uavs);
    setUavCount(snapshot.uavs.length);
  }, []);

  const handleStart = () => setRunning(true);
  const stop = () => {
    setRunning(false);
  };
  const refreshData = () => {
    // reloads the same mock data (replace with fetch if needed)
    const snapshot = data.docs[0];
    setNoFlyZones(snapshot.noFlyZones);
    setUavs(snapshot.uavs);
  };

  return (
    <div className="container-fluid p-0" style={{ height: "100vh" }}>
      <div className="row g-0" style={{ height: "100%" }}>
        {/* Map Section */}
        <div className="col-12 col-lg-9" style={{ height: "100%" }}>
          <BasicMap running={running} uavs={uavs} noFlyZones={noFlyZones} />
        </div>

        {/* Controls Section */}
        <div
          className="col-12 col-lg-3"
          style={{
            height: "100vh",
            overflowY: "auto",
            padding: "12px",
          }}
        >
          <Controls
            running={running}
            setRunning={setRunning}
            stop={stop}
            refreshData={refreshData}
            uavs={uavs}
            uavCount={uavCount}
            setUavCount={setUavCount}
            handleAddUavs={() => {}}
            handleStart={handleStart}
          />
        </div>
      </div>
    </div>
  );
}
