import express from "express";
import {
  createStep,
  getLatestStep,
  getSteps,
  streamStepsSSE,
} from "../controllers/uav.controller.js";

const uavRouter = express.Router();

uavRouter.post("/step", createStep);
uavRouter.get("/latest", getLatestStep);
uavRouter.get("/steps", getSteps);
uavRouter.get("/stream", streamStepsSSE);

export default uavRouter;

    