import cors from "cors";
import express from "express";
import dotenv from "dotenv";
import mongoose from "mongoose";

// Load environment variables
dotenv.config();

import healthCheckRouter from "./routes/healthcheck.routes.js";
import uavRouter from "./routes/uav.routes.js";

const app = express();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static("public"));

// CORS configuration
app.use(
  cors({
    origin: process.env.CORS_ORIGIN?.split(",") || "http://localhost:5173",
    credentials: true,
    methods: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"],
  })
);

mongoose
  .connect(process.env.MONGO_URI, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log("MongoDB connected"))
  .catch((err) => console.error("MongoDB connection error:", err));

// Routes
app.use("/api/v1/healthcheck", healthCheckRouter);
app.use("/api/v1/uavs", uavRouter);

app.get("/", (req, res) => {
  res.send("UTMS Backend Running 🚀");
});

export default app;

