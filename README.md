# 🚀 AstroGuard
## Autonomous Space Traffic Management & Collision Avoidance Platform

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Status](https://img.shields.io/badge/Status-Prototype-orange)
![Platform](https://img.shields.io/badge/Platform-Web%20Dashboard-brightgreen)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

AstroGuard is a physics-grounded, autonomy-ready space traffic management system designed to predict, assess, and mitigate satellite collision risks in increasingly congested Earth orbits.

The platform integrates orbital mechanics, conjunction analysis, maneuver optimization, and real-time visualization into a unified decision-support architecture suitable for research, validation, and future autonomous deployment.

---

## 📌 Problem Statement

The rapid expansion of satellite constellations in Low Earth Orbit (LEO) has resulted in a densely populated and dynamically evolving orbital environment. Space objects travel at relative velocities exceeding 7–8 km/s, where even millimeter-scale debris can cause mission-ending damage.

Current collision avoidance workflows rely on deterministic orbit propagation from Two-Line Element (TLE) data, threshold-based conjunction screening, and human-in-the-loop maneuver planning. These systems scale poorly, generate excessive false positives, and lack global optimization across fuel efficiency, mission continuity, and long-term orbital safety.

---

## 🎯 Core Technical Problem

There is no scalable, autonomous, and decision-aware system capable of continuously predicting conjunction risks and computing optimal avoidance maneuvers under orbital uncertainty and real-time constraints.


---

AstroGuard addresses this gap by combining physics-consistent modeling with modular, autonomy-ready system design.

---

## 🧠 System Objectives

- High-fidelity orbit propagation
- Robust conjunction detection under uncertainty
- Quantitative collision risk assessment
- Fuel-aware maneuver optimization
- Explainable decision visualization
- Architecture compatible with learning-based autonomy

---

## 🛰️ System Architecture Overview

```text
   Public Orbital Data (TLE)
          │
          ▼
     Orbit Propagation Engine
    (SGP4 / Physics-Based Models)
          │
          ▼
    Trajectory Prediction Module
          │
          ▼
    Conjunction Detection Engine
  (Temporal Screening & Pruning)
          │
          ▼
   Collision Risk Assessment
          │
          ▼
  Maneuver Planning & Optimization
          │
          ▼
   Mission Control Web Dashboard
```

---

## ✨ Key Features

- **Physics-based orbit propagation** (SGP4 and custom models)
- **Automated conjunction detection** with uncertainty quantification
- **Collision risk assessment** and alerting
- **Fuel- and mission-aware maneuver optimization**
- **Dual-mode operation:** offline analysis and online real-time pipeline
- **Interactive Mission Control dashboard** for visualization and decision support
- **Modular, service-oriented architecture** for extensibility
- **Stateless, scalable, and cloud-ready deployment**

---

## 🧪 Operating Modes

### Offline Analysis Mode

Enables controlled experimentation using historical or synthetic orbital data. Supports deterministic evaluation of orbit propagation accuracy, conjunction detection sensitivity, and maneuver optimization strategies.

**Offline execution is used for:**
- Scenario generation and dataset creation
- Validation of orbit propagation fidelity
- Benchmarking maneuver strategies (fuel cost, miss distance, orbital deviation)
- Training and evaluation of learning-based policies in reproducible environments

All offline workflows are fully isolated from live telemetry.

### Online Operational Mode

Mission-critical execution pipeline. Continuously propagates active spacecraft orbits, screens predicted trajectories for conjunctions, and evaluates avoidance maneuvers under real-time constraints.

**Online execution provides:**
- Continuous orbit propagation and state updates
- Automated conjunction detection and alerting
- Real-time maneuver feasibility assessment
- Live visualization of predicted and post-maneuver trajectories

The pipeline is stateless, modular, and latency-aware.

---

## 🖥️ Mission Control Dashboard

The Mission Control Dashboard provides an interactive interface for satellite operators to:

- Adjust maneuver parameters
- Toggle autonomous avoidance logic
- View predicted orbital paths
- Receive collision risk alerts
- Compare safe vs unsafe trajectories

All visuals are generated from **computed physical state data** for maximum reliability and transparency.

---

## 🧱 Project Structure


Below is the full project structure with inline descriptions for each file and folder:

```text
protoverse/                                 # Root project directory
│
├── main.py                                # Main entry point; starts API server and orchestrates services
├── requirements.txt                       # Python dependencies for the whole project
├── README.md                              # Project documentation (this file)
│
├── backend/                               # Backend service layer
│   ├── api/                               # API endpoints (FastAPI routers)
│   │   ├── router_conjunctions.py         # Conjunction analysis API (detects close approaches)
│   │   ├── router_maneuver.py             # Maneuver planning API (avoidance maneuvers)
│   │   ├── router_propagate.py            # Orbit propagation API (predicts trajectories)
│   │   ├── router_ssa.py                  # Space Situational Awareness API (aggregates outputs)
│   │   └── router_tle.py                  # TLE ingestion/retrieval API (orbit data)
│   └── models/                            # Database models and ORM
│       └── db.py                          # DB schema for TLEs, propagation, conjunctions
│
├── dashboard/                             # Mission Control web dashboard (UI)
│   ├── index.html                         # Main dashboard HTML entry point
│   └── assets/
│       ├── css/
│       │   └── style.css                  # Dashboard CSS styles
│       ├── img/                           # Dashboard images/icons
│       └── js/
│           └── main.js                    # Dashboard JS (map, alerts, real-time updates)
│
├── data/                                  # Input datasets, generated state vectors, artifacts
│
├── docs/                                  # Documentation, diagrams, screenshots
│   ├── Diagrams/                          # System architecture diagrams
│   └── Screenshots/                       # UI/dashboard screenshots
│
├── ingest/                                # Data ingestion and preprocessing
│   └── tle_fetcher.py                     # Fetches/parses TLE data from public sources
│
├── notebooks/                             # Offline analysis, demos, and validation
│   ├── quick_demo.py                      # Quick demo of core system (offline)
│   ├── test_conjunction_demo.py           # Test harness for conjunction detection
│   └── test_maneuver_optimizer.py         # Test/validate maneuver optimization
│
├── planner/                               # Maneuver planning and optimization
│   └── optimizer.py                       # Computes optimal avoidance maneuvers
│
├── processing/                            # Orbital mechanics and core algorithms
│   ├── conjunction.py                     # Conjunction detection algorithms
│   ├── coord_utils.py                     # Coordinate transforms (ECI/ECEF, etc.)
│   ├── propagate_wrapper.py                # Abstraction for propagation engines (SGP4, etc.)
│   ├── propagator.py                      # Detailed orbit propagation logic
│   └── pruner.py                          # Pruning to reduce computation (KD-tree, etc.)
│
├── service/                               # Service orchestration layer
│   ├── conjunction_service.py             # Orchestrates conjunction analysis workflows
│   ├── maneuver_service.py                # Coordinates maneuver planning logic
│   ├── propagation_service.py             # Manages propagation tasks
│   ├── ssa_service.py                     # Aggregates SSA outputs
│   └── tle_service.py                     # Handles TLE data management
│
├── tests/                                 # Unit and integration tests
│   ├── test_tle_fetcher.py                # Tests for TLE ingestion/parsing
│   └── verification_conjunction_demo.py   # Cross-validation for conjunction detection
```

---

## ⚙️ Technology Stack

| Component              | Technology/Frameworks & Badges                                                                 |
|------------------------|-------------------------------------------------------------------------------------------------------------------|
| Core Language          | ![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy) ![SciPy](https://img.shields.io/badge/SciPy-8CAAE6?logo=scipy) |
| Orbital Mechanics      | ![sgp4](https://img.shields.io/badge/SGP4-darkblue) ![poliastro](https://img.shields.io/badge/poliastro-3776AB?logo=python) custom physics |
| Backend Framework      | ![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)                                                |
| API Style              | ![RESTful](https://img.shields.io/badge/REST-API-green)                                                            |
| Visualization & UI     | ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white) ![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black) ![Plotly](https://img.shields.io/badge/Plotly-3F4F75?logo=plotly) |
| Machine Learning       | ![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?logo=scikit-learn&logoColor=white) ![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?logo=pytorch) (optional) |
| Optimization Paradigm  | ![SciPy](https://img.shields.io/badge/SciPy.optimize-8CAAE6?logo=scipy) custom solvers                             |
| Execution Model        | ![Offline](https://img.shields.io/badge/Offline--Mode-blue) ![Online](https://img.shields.io/badge/Online--Mode-green) |
| Deployment             | ![Local](https://img.shields.io/badge/Local--Deployment-blue) ![Cloud](https://img.shields.io/badge/Cloud--Ready-brightgreen) ![Container](https://img.shields.io/badge/Container--Ready-lightgrey) |

---

## ▶️ Getting Started

### Local Setup

```bash
pip install -r requirements.txt
# To launch the dashboard (if available):
streamlit run dashboard/index.html
```

### Usage

1. **Ingest TLE data:**
  - Use scripts in `ingest/` to fetch and preprocess orbital data.
2. **Run propagation and conjunction analysis:**
  - Use modules in `processing/` and `service/` for orbit propagation and conjunction detection.
3. **Optimize maneuvers:**
  - Use `planner/optimizer.py` for maneuver planning.
4. **Visualize results:**
  - Launch the dashboard for interactive visualization.

---

## ☁️ Deployment

- Web-based dashboard
- Stateless computation pipeline
- Deployable on local ground-station systems and cloud platforms

---

## 🚧 Current Status

- ✅ Physics-based collision detection
- ✅ Realtime satellite TLE ingestion from CelesTrak
- ✅ ML model implemented for prediction of orbital path
- ✅ Reinforcement Learning–based avoidance policy
- ✅ Multi-satellite collision analysis
- ✅ 3D orbital visualization

---

## 🧩 Contributing

Contributions are welcome! Please open issues or submit pull requests for bug fixes, new features, or improvements.

---

## ⚠️ Disclaimer

Only publicly available orbital data is used. No classified or restricted satellite telemetry is accessed.

---

## 🏁 Summary

AstroGuard demonstrates a scalable, explainable, and autonomy-ready approach to satellite collision avoidance. The project emphasizes correct physics, modular system design, and transparent decision support, forming a strong foundation for future AI-driven space traffic management systems.


