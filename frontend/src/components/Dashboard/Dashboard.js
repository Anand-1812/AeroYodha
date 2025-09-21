import React from 'react';
import './styles.css';

const Dashboard = ({ uavs, alerts }) => {
  return (
    <div className="dashboard">
      <h3>Dashboard</h3>
      <p>Active UAVs: {uavs.length}</p>
      <p>Alerts: {alerts.length}</p>
    </div>
  );
};

export default Dashboard;