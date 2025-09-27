import { Router } from "express";
import mongoose, { Schema } from "mongoose";

const uavStateSchema = new Schema(
  {
    step: { type: Number, required: true },
    uavId: { type: String, required: true, ref: "UAV" }, // reference to UAV registry
    x: { type: Number, required: true },
    y: { type: Number, required: true },
    start: { type: String },
    goal: { type: String },
    reached: { type: Boolean, default: false },
    path: [{ type: String }],
  },
  { timestamps: true },
);

export const UAVState = mongoose.model("UAVState", uavStateSchema);
