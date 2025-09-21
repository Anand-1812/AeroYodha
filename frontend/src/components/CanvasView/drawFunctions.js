export const drawBackground = (ctx) => {
  ctx.fillStyle = 'black';
  ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);
};

export const drawUAV = (ctx, x, y, radius, color = 'blue') => {
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, Math.PI * 2);
  ctx.fillStyle = color;
  ctx.fill();
  ctx.closePath();
};

export const drawObstacle = (ctx, x, y, width, height, color = 'red') => {
  ctx.fillStyle = color;
  ctx.fillRect(x, y, width, height);
};

export const drawGeofence = (ctx, points, color = 'rgba(255, 255, 0, 0.5)') => {
  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);
  points.slice(1).forEach(p => ctx.lineTo(p.x, p.y));
  ctx.closePath();
  ctx.fillStyle = color;
  ctx.fill();
};

export const drawPath = (ctx, waypoints, color = 'green', lineWidth = 2) => {
  ctx.beginPath();
  ctx.moveTo(waypoints[0].x, waypoints[0].y);
  waypoints.slice(1).forEach(p => ctx.lineTo(p.x, p.y));
  ctx.strokeStyle = color;
  ctx.lineWidth = lineWidth;
  ctx.stroke();
};

export const drawPriorityLabels = (ctx, uavs, startX, startY) => {
  ctx.font = '12px Arial';
  ctx.fillStyle = 'white';
  uavs.forEach((uav, i) => {
    ctx.fillText(`UAV ${uav.id}: P${uav.priority}`, startX, startY + i * 15);
  });
};