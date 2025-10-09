import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import mongoose from "mongoose";

// Load environment variables
dotenv.config();

// Routes
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
    origin: process.env.CORS_ORIGIN?.split(",") || ["http://localhost:5173"],
    credentials: true,
    methods: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"],
  })
);

// MongoDB Connection
mongoose
  .connect(process.env.MONGO_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .then(() => console.log("✅ MongoDB connected"))
  .catch((err) => console.error("❌ MongoDB connection error:", err));

// Routes
// Health check
app.use("/api/v1/healthcheck", healthCheckRouter);
// This route will receive demo-like grid data (rows=12, cols=8)
app.use("/api/v1/uavs", uavRouter);

// Root
app.get("/", (req, res) => {
  res.send("🛩️ UTMS Backend Running (Demo Grid Mode)");
});

app.use((req, res) => {
  res.status(404).json({ message: "Route not found" });
});

export default app;

