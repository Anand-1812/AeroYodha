import { Router } from "express";
import { UAV } from "../models/uav.model.js";
import { UAVState } from "../models/uavState.model.js";

const uavRouter = Router();

//
// 📌 UAV Registry Routes (CRUD)
//

// Get all UAVs
uavRouter.get("/", async (req, res) => {
  try {
    const uavs = await UAV.find();
    res.json(uavs);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Get UAV by ID
uavRouter.get("/:id", async (req, res) => {
  try {
    const uav = await UAV.findById(req.params.id);
    if (!uav) return res.status(404).json({ message: "UAV not found" });
    res.json(uav);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Create new UAV
uavRouter.post("/", async (req, res) => {
  try {
    const uav = new UAV(req.body);
    await uav.save();
    res.status(201).json(uav);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// Update UAV
uavRouter.put("/:id", async (req, res) => {
  try {
    const uav = await UAV.findByIdAndUpdate(req.params.id, req.body, {
      new: true,
    });
    if (!uav) return res.status(404).json({ message: "UAV not found" });
    res.json(uav);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// Delete UAV
uavRouter.delete("/:id", async (req, res) => {
  try {
    const uav = await UAV.findByIdAndDelete(req.params.id);
    if (!uav) return res.status(404).json({ message: "UAV not found" });
    res.json({ message: "UAV deleted successfully" });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

//
// 📌 UAV Simulation State Routes
//

// Batch insert simulation states
uavRouter.post("/batch", async (req, res) => {
  try {
    const { step, uavs } = req.body;

    if (!uavs || !Array.isArray(uavs)) {
      return res.status(400).json({ message: "Invalid UAV data" });
    }

    const docs = uavs.map((u) => ({
      step,
      uavId: u.id,
      x: u.x,
      y: u.y,
      start: u.start,
      goal: u.goal,
      reached: u.reached,
      path: u.path,
    }));

    await UAVState.insertMany(docs, { ordered: false });

    res.status(201).json({ message: "UAV states saved", count: docs.length });
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// Get all states for a specific UAV
uavRouter.get("/states/:uavId", async (req, res) => {
  try {
    const states = await UAVState.find({ uavId: req.params.uavId }).sort("step");
    res.json(states);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Get all states at a specific step
uavRouter.get("/states", async (req, res) => {
  try {
    const { step } = req.query;
    if (!step) return res.status(400).json({ message: "Step is required" });

    const states = await UAVState.find({ step: Number(step) });
    res.json(states);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

export default uavRouter;
