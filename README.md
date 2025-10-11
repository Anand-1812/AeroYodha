# 🛩️ UAV Simulation & Path Planning

A full-stack ***UAV (Drone) simulation system*** that models UAV movement on a real or grid-based map, plans optimal paths, and streams real-time flight steps to a frontend dashboard. Built with **Python**, **Node.js**, **Express**, **MongoDB**, and **React**, this project replicates key features of UAV path planning including **simulation**, **real-time updates**, and **visualization**.

---

## 📸 Demo

![Simulation](https://user-images.githubusercontent.com/placeholder/simulation-demo.png)

<img width="1900" alt="Simulation Map" src="https://user-images.githubusercontent.com/placeholder/map-demo.png" />

<img width="1900" alt="Frontend View" src="https://user-images.githubusercontent.com/placeholder/frontend-demo.png" />

---

## 🚀 Live Demo
🌐 *Hosted Link*: [UAV Simulation](https://your-deployed-link.com)

---

## ⚡ Tech Stack

**Backend**
- [Node.js](https://nodejs.org/) – JavaScript runtime
- [Express.js](https://expressjs.com/) – Web framework
- [Mongoose](https://mongoosejs.com/) – MongoDB object modeling

**Frontend**
- [React](https://reactjs.org/) – UI library
- [TailwindCSS](https://tailwindcss.com/) – Styling framework

**Simulation**
- [Python 3](https://www.python.org/) – Simulation scripts
- [NumPy](https://numpy.org/) – Numerical computations
- [Matplotlib](https://matplotlib.org/) – Visualization
- [NetworkX](https://networkx.org/) – Graph & path planning

**Database & Cloud Services**
- [MongoDB Atlas](https://www.mongodb.com/atlas) – Cloud database

---

## ✨ Features

- 🛰️ ***UAV Path Simulation*** – Step-by-step UAV movement in a grid or map
- 🗺️ ***Path Planning Algorithm*** – Computes optimal paths avoiding no-fly zones (e.g., using A* or Dijkstra's)
- 🌐 ***Real-time Updates*** – Server-Sent Events (**SSE**) streaming flight data to the frontend
- 🔄 ***Backend API*** – Robust API endpoints: `POST /step`, `GET /latest`, `GET /steps`, `GET /stream`
- 🖥️ ***Frontend Visualization*** – Interactive map displaying the UAV path, current position, and no-fly zones
- 📦 ***Sample Data Support*** – Option to run the frontend independently for testing/development
- 💻 ***Responsive UI*** – Works well on desktop and mobile devices

---

## 📂 Project Structure

UAV\_Simulation/
├── backend/
│ ├── src/
│ │ ├── controllers/ # API controllers for flight steps
│ │ ├── db/ # Database connection (MongoDB)
│ │ ├── models/ # MongoDB schemas (FlightStep)
│ │ ├── routes/ # Express routes
│ │ ├── utils/ # Utility functions
│ │ ├── app.js # Express app setup
│ │ └── index.js # Entry point
│ ├── package.json
│ └── package-lock.json
├── frontend/
│ ├── src/
│ │ ├── assets/ # Images, icons
│ │ ├── components/ # UI components (controls, map, simulation view)
│ │ ├── App.jsx # Main app component
│ │ ├── main.jsx # React entry point
│ │ ├── index.css
│ │ └── app.css
│ ├── package.json
│ └── public/
├── UAV\_Traffic/
│ ├── scripts/ # Python simulation scripts (path planning logic)
│ └── results/ # Simulation outputs
├── requirements.txt # Python dependencies
├── venv/ # Python virtual environment (optional)
└── README.md


---

## ⚙️ Installation & Setup
Follow these steps to run the project locally:

1. *Clone the repository*

git clone [https://github.com/your-username/uav-simulation.git](https://github.com/your-username/uav-simulation.git)
cd uav-simulation

2. *Setup Backend*
cd backend
npm install

3. Create a .env file in the backend/ directory and add the following:
# MongoDB Atlas
MONGO_URI=your_mongodb_connection_string

# Express server port
PORT=5000

4. Run the backend server
npm run dev

5. Set up python simulation

python -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
cd UAV_Traffic
python scripts/demo.py

Note: This script will start running the simulation, pushing steps to the backend API.

6. Run frontend
cd frontend
npm i
npm run dev

🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to fork this repo and submit a pull request.
