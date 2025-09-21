import React from 'react';
import './styles.css';

const Controls = ({ onAddUAV, onSwitchScenario }) => {
  return (
    <div className="controls">
      <button onClick={onAddUAV}>Add UAV</button>
      <select onChange={onSwitchScenario}>
        <option>Urban</option>
        <option>Rural</option>
      </select>
    </div>
  );
};

export default Controls;