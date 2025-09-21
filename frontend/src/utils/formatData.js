export const formatUAVData = (rawData) => rawData.map(item => ({
  ...item,
  x: parseFloat(item.x),
  y: parseFloat(item.y)
}));