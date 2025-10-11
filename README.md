# 🛩️ UAV Simulation & Path Planning

A full-stack *UAV (Drone) simulation system* that models UAV movement on a real or grid-based map, plans optimal paths, and streams real-time flight steps to a frontend dashboard. Built with *Python, Node.js, Express, MongoDB, and React*, this project replicates key features of UAV path planning including *simulation, real-time updates, and visualization*.

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

- 🛰️ *UAV Path Simulation* – Step-by-step UAV movement in a grid or map  
- 🗺️ *Path Planning Algorithm* – Computes optimal paths avoiding no-fly zones  
- 🌐 *Real-time Updates* – Server-Sent Events (SSE) streaming to frontend  
- 🔄 *Backend API* – `POST /step`, `GET /latest`, `GET /steps`, `GET /stream`  
- 🖥️ *Frontend Visualization* – Interactive map displaying UAV paths  
- 📦 *Sample Data Support* – Can run frontend without backend for testing  
- 💻 *Responsive UI* – Works on desktop and mobile  

---

## 📂 Project Structure

UAV_Simulation/
├── backend/
│ ├── src/
│ │ ├── controllers/ # API controllers
│ │ ├── db/ # Database connection
│ │ ├── models/ # MongoDB schemas
│ │ ├── routes/ # Express routes
│ │ ├── utils/ # Utility functions
│ │ ├── app.js # Express app
│ │ └── index.js # Entry point
│ ├── package.json
│ └── package-lock.json
├── frontend/
│ ├── src/
│ │ ├── assets/ # Images, icons
│ │ ├── components/ # UI components (controls, map, simulation)
│ │ ├── App.jsx # Main app component
│ │ ├── main.jsx # React entry point
│ │ ├── index.css
│ │ └── app.css
│ ├── package.json
│ └── public/
├── UAV_Traffic/
│ ├── scripts/ # Python simulation scripts
│ └── results/ # Simulation outputs
├── requirements.txt # Python dependencies
├── venv/ # Python virtual environment
└── README.md


## ⚙️ Installation & Setup

**1. Clone the repository**
```bash
git clone https://github.com/your-username/uav-simulation.git
cd uav-simulation

**1. Clone the repository**
```bash
git clone https://github.com/your-username/uav-simulation.git
cd uav-simulation

2. Setup Backend

cd backend
npm install

3. Create a .env file in backend/ (use .env.example as template)

# MongoDB Atlas
MONGO_URI=your_mongodb_connection_string

# Express server port
PORT=5000

4. Run the backend server

npm start

5. Setup Python Simulation

cd UAV_Traffic
python3 -m venv venv      # optional if not already created
source venv/bin/activate
pip install -r ../requirements.txt
python scripts/demo.py

6. Run Frontend

cd frontend
npm install
npm run dev

Open your browser at: http://localhost:5173
🛠️ Future Enhancements

    ✅ 3D visualization of UAV flight

    ✅ Real GPS coordinates integration

    ✅ Multi-UAV support

    ✅ Collision detection and dynamic no-fly zones

    ✅ Historical mission storage and replay

🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to fork this repo and submit a pull request.
📜 License

This project is licensed under the MIT License – free to use, modify, and distribute.
💡 Developer

Made with ❤️ by Anand
