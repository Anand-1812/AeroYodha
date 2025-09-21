import React from 'react';
import './styles.css';

const PriorityQueue = ({ uavs }) => {
  const sortedUAVs = [...uavs].sort((a, b) => a.priority - b.priority);
  return (
    <ul className="priority-queue">
      {sortedUAVs.map((uav) => (
        <li key={uav.id} style={{ color: uav.priorityColor }}>
          UAV {uav.id}: Priority {uav.priority}
        </li>
      ))}
    </ul>
  );
};

export default PriorityQueue;
