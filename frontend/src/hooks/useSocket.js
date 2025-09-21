import { useState, useEffect } from 'react';
import socket from '../services/socketService';

export const useSocket = () => {
  const [uavs, setUAVs] = useState([]);
  const [obstacles, setObstacles] = useState([]);
  const [geofences, setGeofences] = useState([]);
  const [paths, setPaths] = useState([]);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    socket.on('uavUpdate', (data) => {
      setUAVs(data.uavs.map(uav => ({
        ...uav,
        priorityColor: uav.priority < 3 ? 'red' : 'blue' // Example coloring
      })));
      setPaths(data.paths);
      // Similarly for others
    });
    return () => socket.off('uavUpdate');
  }, []);

  return { uavs, obstacles, geofences, paths, alerts };
};