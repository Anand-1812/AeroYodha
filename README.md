# 🛩️ UAV Path Planning & Simulation Project

A full-stack drone simulation system that models UAV movement on a real or grid-based map, plans optimal paths, and streams real-time flight steps to a frontend dashboard.

---

## 🚀 Overview

This project simulates UAV (Unmanned Aerial Vehicle) navigation with path planning, real-time updates, and backend data streaming.

The system consists of:
1. **Simulation Engine (Python)** — Builds a map grid, runs path planning, and simulates UAV motion.
2. **Backend Server (Node.js + Express)** — Receives UAV steps, stores them, and provides real-time streaming via SSE.
3. **Frontend Dashboard (React)** — Visualizes UAV position, path, and live telemetry.

---

## 🧩 Architecture

demo.py ─▶ simulate_uav.py ─▶ path_planning.py
│
▼
backend_connector.py ─▶ Express Server ─▶ MongoDB
│
▼
Frontend (React)


---

## 🧠 Core Features

### 🛰️ Simulation
- Builds a **grid graph** representing the area.
- Computes an **optimal path** avoiding no-fly zones.
- Simulates UAV step-by-step movement.
- Sends data to backend after each step.

### 🖥️ Backend
- Built with **Express + MongoDB**.
- Exposes REST and SSE routes:
  - `POST /step` → Store UAV step.
  - `GET /steps` → Get all steps.

### 📊 Frontend
- Built with **React** + **leafletjs**.
- Displays UAV path and live movement.

---

## ⚙️ Tech Stack

| Layer | Technologies |
|-------|---------------|
| Simulation | Python, NumPy, Matplotlib, NetworkX |
| Backend | Node.js, Express.js, MongoDB |
| Frontend | React, Vite/CRA, BootStrap, leafletjs |
| Communication | REST API, SSE (Server-Sent Events) |

