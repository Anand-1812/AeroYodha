// controllers/simulationController.js
import { StepSnapshot } from "../models/uav.model.js";

/**
 * POST /api/simulation/step
 * Body: { step: number, uavs: [...], noFlyZones: [...], meta?: {...} }
 * Save a new step snapshot (replaces previous step)
 */
export const createStep = async (req, res) => {
  try {
    const { step, uavs = [], noFlyZones = [], meta = {} } = req.body;

    if (typeof step !== "number") {
      return res.status(400).json({ ok: false, message: "Missing or invalid 'step' (number)" });
    }

    // Replace previous step with fixed _id
    const stepDoc = { step, uavs, noFlyZones, meta, _id: "latest_step" };
    await StepSnapshot.replaceOne(
      { _id: "latest_step" }, // find the document with this ID
      stepDoc,                // new data
      { upsert: true }        // insert if doesn't exist
    );

    return res.status(201).json({ ok: true, doc: stepDoc });
  } catch (err) {
    console.error("createStep error:", err);
    return res.status(500).json({ ok: false, message: "Internal server error" });
  }
};

/**
 * GET /api/simulation/latest
 * Returns the most recent step
 */
export const getLatestStep = async (req, res) => {
  try {
    const latest = await StepSnapshot.findOne({ _id: "latest_step" }).lean().exec();
    if (!latest) return res.status(404).json({ ok: false, message: "No snapshot found" });
    return res.json({ ok: true, latest });
  } catch (err) {
    console.error("getLatestStep error:", err);
    return res.status(500).json({ ok: false, message: "Internal server error" });
  }
};

/**
 * GET /api/simulation/steps?limit=50&page=1
 * Paged history for UI replay
 * Note: If you only keep latest step, this will just return one document
 */
export const getSteps = async (req, res) => {
  try {
    const limit = Math.min(parseInt(req.query.limit || "100", 10), 1000);
    const page = Math.max(parseInt(req.query.page || "1", 10), 1);
    const skip = (page - 1) * limit;

    const docs = await StepSnapshot.find()
      .sort({ step: 1, createdAt: 1 }) // chronological
      .skip(skip)
      .limit(limit)
      .lean()
      .exec();

    const total = await StepSnapshot.countDocuments();

    return res.json({ ok: true, total, page, limit, docs });
  } catch (err) {
    console.error("getSteps error:", err);
    return res.status(500).json({ ok: false, message: "Internal server error" });
  }
};

/**
 * SSE endpoint to stream snapshots live to frontend
 * GET /api/simulation/stream
 */
export const streamStepsSSE = async (req, res) => {
  // set headers for SSE
  res.set({
    Connection: "keep-alive",
    "Cache-Control": "no-cache",
    "Content-Type": "text/event-stream",
  });
  res.flushHeaders();

  // ping every 15s to keep connection alive
  const ping = setInterval(() => {
    res.write(`: ping\n\n`);
  }, 15000);

  // poll DB every 500ms for latest step
  let lastId = null;
  const poll = setInterval(async () => {
    try {
      const latest = await StepSnapshot.findOne({ _id: "latest_step" }).lean().exec();
      if (!latest) return;
      const latestId = String(latest._id);
      if (latestId !== lastId) {
        lastId = latestId;
        res.write(`event: step\n`);
        res.write(`data: ${JSON.stringify(latest)}\n\n`);
      }
    } catch (err) {
      console.error("SSE poll error:", err);
    }
  }, 500);

  // cleanup on client disconnect
  req.on("close", () => {
    clearInterval(poll);
    clearInterval(ping);
    res.end();
  });
};
