// models/StepSnapshot.js
import mongoose from "mongoose";
const { Schema } = mongoose;

// Matches each UAV dict from demo.py exactly
const uavSchema = new Schema(
  {
    id: { type: Number, required: true },
    x: { type: Number, required: true },
    y: { type: Number, required: true },
    start: { type: [Number], required: true },  // [row, col]
    goal: { type: [Number], required: true },   // [row, col]
    reached: { type: Boolean, default: false },
    path: { type: [[Number]], default: [] },    // list of [row, col]
  },
  { _id: false }
);

const stepSchema = new Schema(
  {
    step: { type: Number, required: true },
    uavs: { type: [uavSchema], default: [] },
    noFlyZones: { type: [[Number]], default: [] },
  },
  { timestamps: true }
);

stepSchema.index({ createdAt: 1 }, { expireAfterSeconds: 3600 });
export const StepSnapshot = mongoose.model("StepSnapshot", stepSchema);

