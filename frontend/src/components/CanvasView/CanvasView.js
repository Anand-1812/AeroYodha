import React, { useRef, useEffect } from 'react';
import { useAnimation } from '../../hooks/useAnimation';
import * as draw from './drawFunctions';
import './styles.css';

const CanvasView = ({ uavs, obstacles, geofences, paths }) => {
  const canvasRef = useRef(null);

  const drawFrame = (ctx) => {
    draw.drawBackground(ctx);
    geofences.forEach(geo => draw.drawGeofence(ctx, geo.points));
    obstacles.forEach(obs => draw.drawObstacle(ctx, obs.x, obs.y, obs.width, obs.height));
    paths.forEach(path => draw.drawPath(ctx, path.waypoints));
    uavs.forEach(uav => draw.drawUAV(ctx, uav.x, uav.y, 10, uav.priorityColor));
    draw.drawPriorityLabels(ctx, uavs, 10, 10); // Overlay priorities if needed
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }, []);

  useAnimation(canvasRef, drawFrame);

  return <canvas ref={canvasRef} className="canvas" />;
};

export default CanvasView;