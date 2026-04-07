# 🚚 Green Route Optimizer: Sustainable Logistics Environment

**An OpenEnv-compatible Reinforcement Learning environment for optimizing carbon-efficient delivery networks.**

---

## 🌿 Project Overview
Traditional logistics prioritize speed and cost above all else. **Green Route Optimizer** introduces a new paradigm: **Sustainability-First Logistics**. This environment challenges AI agents to deliver packages while strictly managing battery levels and minimizing carbon footprints.

Built for the **Meta x PyTorch OpenEnv Hackathon**, this project provides a high-fidelity simulation of an urban delivery hub equipped with both Electric and Diesel fleets.

### Key Features:
* **Dynamic Physics Engine:** Battery consumption is calculated based on distance traveled and payload weight.
* **Carbon Penalization:** Diesel vehicles incur high $CO_2$ costs, forcing agents to prioritize electric fleets or optimize diesel routes.
* **API-First Architecture:** Built with FastAPI, allowing any RL agent to interact with the environment via REST.
* **OpenEnv Native:** Fully compliant with the OpenEnv specification, including `openenv.yaml` and Docker containerization.

---

## 🛠 Tech Stack
* **Language:** Python 3.10+
* **Framework:** FastAPI & Uvicorn
* **Data Validation:** Pydantic
* **Testing:** Pytest
* **Deployment:** Docker & OpenEnv

---

## 📂 Project Structure
```text
green_route_hackathon/
├── agents/             # AI players (Random & Heuristic baselines)
├── src/
│   ├── api/            # FastAPI endpoints and schemas
│   └── core/           # Physics engine, Reward logic, and Entities
├── tests/              # Automated logic and math verification
├── Dockerfile          # Container configuration for deployment
├── openenv.yaml        # OpenEnv framework manifest
├── pyproject.toml      # Project metadata
└── requirements.txt    # Project dependencies