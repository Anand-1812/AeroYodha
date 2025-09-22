import { Router } from "express";
import { UAV } from "../models/uav.model.js"; // adjust path if needed

const uavRouter = Router();

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
    const uav = await UAV.findByIdAndUpdate(req.params.id, req.body, { new: true });
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

export default uavRouter;

