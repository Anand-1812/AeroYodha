import { useEffect } from 'react';

export const useAnimation = (canvasRef, drawFrame) => {
  useEffect(() => {
    let animationFrameId;
    const render = () => {
      const ctx = canvasRef.current?.getContext('2d');
      if (ctx) {
        ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
        drawFrame(ctx);
      }
      animationFrameId = window.requestAnimationFrame(render);
    };
    render();
    return () => window.cancelAnimationFrame(animationFrameId);
  }, [drawFrame]);
};