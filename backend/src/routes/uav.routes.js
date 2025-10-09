// routes/simulation.js
import express from "express";
import {
  createStep,
  getLatestStep,
  getSteps,
  streamStepsSSE,
} from "../controllers/simulationController.js";

const uavRouter = express.Router();

router.post("/step", createStep);
router.get("/latest", getLatestStep);
router.get("/steps", getSteps);
router.get("/stream", streamStepsSSE);

export default uavRouter;

