# 🚀 Space Collision Avoidance System

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
```++++++++++++++++++++++++++++++++++++++++++++++++
---

## 🖥️ Mission Control Dashboard

The system follows a strict pipeline from raw orbital data to visual decision support:
- Adjust maneuver parameters
- Toggle autonomous avoidance logic
- View predicted orbital paths
- Receive collision risk alerts
- Compare safe vs unsafe trajectories

All visuals are generated from **computed physical state data**.

---

## 🧱 Project Structure


collison/
├── collison/              # Core simulation & collision logic
├── examples/              # Example runs
├── gui/                   # Web-based dashboard
│   ├── app.py
│   ├── simulator_bridge.py
│   └── **init**.py
├── requirements.txt
The web-based dashboard serves as the central interface for operators.
└── README.md


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

### AI / Acceleration (Planned)
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
* ✅ Real satellite TLE ingestion from CelesTrak
* ✅ ML model planned (architecture ready) 

* Reinforcement Learning–based avoidance policy
* Multi-satellite collision analysis
* 3D orbital visualization

---

## ⚠️ Disclaimer

No classified or restricted satellite telemetry is used.

---

## 🏁 Note
This project emphasizes **system design, explainability, and decision support**, demonstrating how collision risks can be evaluated before executing real satellite maneuvers.

```