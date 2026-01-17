# 🚀 AstroGuard — Autonomous Space Traffic Management & Collision Avoidance Platform

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Status](https://img.shields.io/badge/Status-Prototype-orange)
![Platform](https://img.shields.io/badge/Platform-Web%20Dashboard-brightgreen)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

A **real-time satellite collision prediction and avoidance decision-support system** built using orbital propagation, physics-based modeling, and an interactive mission-control-style web dashboard.

## ✨ What This Project Does (MVP)

- Predicts **future satellite trajectories**
- Detects **potential collision / conjunction events**
- Computes **safe vs unsafe paths**
- Visualizes decisions in a **Mission Control–style dashboard**
- Designed to integrate **AI models** in later stages

This is a **decision-support system**, not a game or animation.

## 🛰️ MVP System Flow

A **real-time satellite collision prediction and decision-support system**. This project utilizes orbital propagation and physics-based modeling to detect conjunction events and visualize avoidance maneuvers via an interactive Mission Control dashboard.
Satellite Orbital Data (TLE)
↓
Orbit Propagation
Trajectory Prediction
↓
Collision Risk Detection
* **🛰️ Orbit Propagation:** Predicts future satellite trajectories based on TLE data.
* **💥 Collision Detection:** Identifies potential conjunction events (close approaches) in real-time.
* **🛡️ Avoidance Logic:** Computes safe vs. unsafe paths to assist operators.
* **🖥️ Interactive Dashboard:** A Mission Control-style interface to visualize decisions.
* **🧠 AI-Ready:** Architecture designed to integrate Reinforcement Learning models in future iterations.


## 🖥️ Mission Control Dashboard

The Mission Control Dashboard provides an interactive interface for satellite operators to:

- **Adjust maneuver parameters**
- **Toggle autonomous avoidance logic**
- **View predicted orbital paths**
- **Receive collision risk alerts**
- **Compare safe vs unsafe trajectories**

All visuals are generated from **computed physical state data** for maximum reliability and transparency.

---


## 🧱 Project Structure

```
protoverse/
├── main.py                  # 🚀 System orchestrator & entry point
├── requirements.txt         # 📦 Python dependencies
├── README.md                # 📖 Project documentation
├── backend/                 # 🛰️ FastAPI backend (API layer)
│   ├── api/
│   │   ├── router_conjunctions.py   # 🔗 Conjunction event API endpoints
│   │   ├── router_maneuver.py       # 🛠️ Maneuver planning API endpoints
│   │   ├── router_propagate.py      # 📡 Orbit propagation API endpoints
│   │   ├── router_ssa.py            # 🛰️ Space situational awareness API
│   │   ├── router_tle.py            # 📑 TLE ingestion & management API
│   │   └── __pycache__/             # ⚡ Python bytecode cache
│   └── models/
│       ├── db.py                    # 🗄️ Database models & ORM
│       └── __pycache__/             # ⚡ Python bytecode cache
├── dashboard/               # 🖥️ Web dashboard (frontend UI)
│   ├── index.html                  # 🌐 Main dashboard HTML
│   └── assets/
│       ├── css/
│       │   └── style.css           # 🎨 Dashboard styles
│       ├── img/                    # 🖼️ UI images & icons
│       └── js/
│           └── main.js             # ⚙️ Dashboard interactivity logic
├── data/                    # 📊 Data files & resources
├── docs/                    # 📚 Documentation, diagrams, screenshots
│   ├── Diagrams/                   # 🗺️ System architecture diagrams
│   └── Screenshots/                # 📸 UI and result screenshots
├── ingest/                  # 📥 Data ingestion scripts
│   ├── tle_fetcher.py              # 🔄 TLE data fetcher & parser
│   └── __pycache__/                # ⚡ Python bytecode cache
├── notebooks/               # 📓 Jupyter & Python demo notebooks
│   ├── quick_demo.py               # 🚦 Quick system demo
│   ├── test_conjunction_demo.py    # 🧪 Conjunction detection demo
│   └── test_maneuver_optimizer.py  # 🧪 Maneuver optimization demo
├── planner/                 # 🧠 Maneuver optimization logic
│   ├── optimizer.py                # 🛠️ Maneuver optimization algorithms
│   └── __pycache__/                # ⚡ Python bytecode cache
├── processing/              # ⚙️ Core processing modules
│   ├── conjunction.py              # 🔗 Conjunction detection logic
│   ├── coord_utils.py              # 🗺️ Coordinate transformation utilities
│   ├── propagate_wrapper.py        # 📡 Orbit propagation wrapper
│   ├── propagator.py               # 📡 Physics-based propagator
│   ├── pruner.py                   # ✂️ Data pruning & filtering
│   └── __pycache__/                # ⚡ Python bytecode cache
├── service/                 # 🛎️ Service layer (business logic)
│   ├── conjunction_service.py      # 🔗 Conjunction event service
│   ├── maneuver_service.py         # 🛠️ Maneuver planning service
│   ├── propagation_service.py      # 📡 Propagation service logic
│   ├── ssa_service.py              # 🛰️ SSA service logic
│   ├── tle_service.py              # 📑 TLE management service
│   └── __pycache__/                # ⚡ Python bytecode cache
├── tests/                   # 🧪 Test scripts & verification
│   ├── test_tle_fetcher.py         # 🧪 TLE fetcher unit tests
│   └── verification_conjunction_demo.py # 🧪 Conjunction verification demo
```

---


### Core
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy)
![SciPy](https://img.shields.io/badge/SciPy-8CAAE6?logo=scipy)

### Orbital Mechanics
![Orbit](https://img.shields.io/badge/Orbital%20Propagation-SGP4-darkblue)

### Visualization & UI
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?logo=plotly)

### ML / Acceleration 
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch)
![GPU](https://img.shields.io/badge/GPU-RTX%204050-green?logo=nvidia)

---

## 🔄 Live / Offline 

**Offline**
- Scenario generation
- Dataset creation

**Online**
- Orbit propagation
- Collision detection
- Avoidance decision
- Real-time visualization

---

## ▶️ Run Locally

```bash
pip install -r requirements.txt
streamlit run gui/app.py
````

---

## ☁️ Deployment (MVP)

* Web-based Streamlit dashboard
* Stateless computation pipeline
* Deployable on:

  * Hugging Face Spaces
  * Local ground-station systems

---

## 🚧 Current Status

* ✅ Physics-based collision detection
* ✅ Realtime satellite TLE ingestion from CelesTrak
* ✅ ML model implemented for prediction of orbital path

* ✅ Reinforcement Learning–based avoidance policy
* ✅ Multi-satellite collision analysis
* ✅ 3D orbital visualization

---

## ⚠️ Disclaimer

No classified or restricted satellite telemetry is used.

---

## 🏁 Note
This project emphasizes **system design, explainability, and decision support**, demonstrating how collision risks can be evaluated before executing real satellite maneuvers.
