import mongoose, { Schema } from "mongoose";

// UAV model
const uavSchema = new Schema({
  id: { type: Number, required: true },
  x: { type: Number, required: true },
  y: { type: Number, required: true },
  start: { type: String, required: true },
  goal: { type: String, required: true },
  reached: { type: Boolean, default: false },
  path: [{ type: String }]
});

const stepSchema = new Schema(
  {
    step: { type: Number, required: true },
    uavs: [uavSchema],

    // for geo fencing
    noFlyZones: [{ type: String }]
  },
  { timestamps: true }
);

// Auto-delete after 2 mins
stepSchema.index({ createdAt: 1 }, { expireAfterSeconds: 120 });

export const UAV = mongoose.model("StepSnapshot", stepSchema);

