import mongoose, { Schema } from "mongoose";

const uavSchema = new Schema({
  id: { type: Number, required: true },       // UAV id from sim
  x: { type: Number, required: true },
  y: { type: Number, required: true },
  start: { type: String, required: true },
  goal: { type: String, required: true },
  reached: { type: Boolean, default: false },
  path: [{ type: String }]                    // array of node ids
});

const stepSchema = new Schema(
  {
    step: { type: Number, required: true },   // simulation timestep
    uavs: [uavSchema]                         // array of UAV states
  },
  { timestamps: true } // adds createdAt & updatedAt
);

stepSchema.index({ createdAt: 1 }, { expireAfterSeconds: 120 });
export const UAV = mongoose.model("StepSnapshot", stepSchema);
