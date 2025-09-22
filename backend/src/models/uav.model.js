import mongoose, { Schema } from "mongoose";

// UAV Schema
const uavSchema = new Schema(
  {
    _id: { type: String, required: true }, // UAV ID
    type: {
      type: String,
      enum: ["commercial", "emergency", "recreational"],
      required: true
    },
    status: {
      type: String,
      enum: ["idle", "flying", "emergency", "maintenance"],
      default: "idle"
    },
    latitude: { type: Number, default: null },
    longitude: { type: Number, default: null },
    altitude: { type: Number, default: null },
    batteryLevel: { type: Number, default: 100 },
  },
  { timestamps: true } // adds createdAt and updatedAt automatically
);

export const UAV = mongoose.model("UAV", uavSchema);

