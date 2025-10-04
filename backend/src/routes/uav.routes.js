import { Router } from "express";
import { UAV } from "../models/uav.model.js"; // now it's snapshot-based

const uavRouter = Router();

// Get all step snapshots
uavRouter.get("/", async (req, res) => {
  try {
    const snapshots = await UAV.find();
    res.json(snapshots);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Get snapshot by step
uavRouter.get("/:step", async (req, res) => {
  try {
    const snapshot = await UAV.findOne({ step: req.params.step });
    if (!snapshot) return res.status(404).json({ message: "Snapshot not found" });
    res.json(snapshot);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

// Create new snapshot
uavRouter.post("/", async (req, res) => {
  try {
    const snapshot = new UAV(req.body);
    await snapshot.save();
    res.status(201).json(snapshot);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// Update snapshot by step
uavRouter.put("/:step", async (req, res) => {
  try {
    const snapshot = await UAV.findOneAndUpdate(
      { step: req.params.step },
      req.body,
      { new: true }
    );
    if (!snapshot) return res.status(404).json({ message: "Snapshot not found" });
    res.json(snapshot);
  } catch (err) {
    res.status(400).json({ message: err.message });
  }
});

// Delete snapshot by step
uavRouter.delete("/:step", async (req, res) => {
  try {
    const snapshot = await UAV.findOneAndDelete({ step: req.params.step });
    if (!snapshot) return res.status(404).json({ message: "Snapshot not found" });
    res.json({ message: "Snapshot deleted successfully" });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

export default uavRouter;

