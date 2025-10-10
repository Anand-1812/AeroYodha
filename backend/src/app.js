import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import mongoose from "mongoose";

// Load environment variables
dotenv.config();

// Routes
import healthCheckRouter from "./routes/healthcheck.routes.js";
import uavRouter from "./routes/uav.routes.js";
import { StepSnapshot } from "./models/StepSnapshot.js"; // ⬅️ import your model

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
  .then(async () => {
    console.log("✅ MongoDB connected");

    // 🧹 TTL Index Cleanup (only runs if TTL index exists)
    try {
      const indexes = await StepSnapshot.collection.indexes();
      const ttlIndex = indexes.find((i) => i.expireAfterSeconds);
      if (ttlIndex) {
        await StepSnapshot.collection.dropIndex(ttlIndex.name);
        console.log(`🧹 Dropped TTL index: ${ttlIndex.name}`);
      } else {
        console.log("✅ No TTL index found on StepSnapshot");
      }
    } catch (err) {
      console.error("⚠️ TTL index cleanup error:", err.message);
    }
  })
  .catch((err) => console.error("❌ MongoDB connection error:", err));

// Routes
app.use("/api/v1/healthcheck", healthCheckRouter);
app.use("/api/v1/uavs", uavRouter);

// Root
app.get("/", (req, res) => {
  res.send("🛩️ UTMS Backend Running (Demo Grid Mode)");
});

app.use((req, res) => {
  res.status(404).json({ message: "Route not found" });
});

export default app;
