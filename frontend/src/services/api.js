export const getMockData = () => ({
  uavs: [{ id: 1, x: 100, y: 100, priority: 1 }],
  obstacles: [{ x: 200, y: 200, width: 50, height: 50 }],
  geofences: [{ points: [{x:0,y:0}, {x:100,y:0}, {x:100,y:100}, {x:0,y:100}] }],
  paths: [{ waypoints: [{x:100,y:100}, {x:300,y:300}] }]
});