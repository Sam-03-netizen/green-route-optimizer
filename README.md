# 🚚 Green Route Optimizer: Sustainable Logistics OpenEnv

**Green Route Optimizer** is an OpenEnv-compatible benchmark environment for evaluating agents on sustainable logistics decision-making tasks.

Built for the **Meta x PyTorch OpenEnv Hackathon**, this project provides a benchmark environment for evaluating AI agents on a practical urban fleet optimization problem.

---

## 🌍 Why this environment matters

Real-world logistics systems often optimize only for **speed** or **cost**.  
This environment introduces a more realistic objective:

- Deliver as many orders as possible
- Avoid stranding vehicles
- Minimize diesel usage and carbon emissions
- Handle multiple delivery tasks with increasing difficulty

This makes the environment useful for benchmarking agents on **real-world decision-making under operational constraints**.

---

## ✨ Core Features

- Real-world logistics task simulation
- Mixed fleet of electric and diesel trucks
- Distance-based battery drain
- Carbon penalty for diesel trucks
- FastAPI-based API interaction
- OpenEnv-style `reset / step / state / grade` endpoints
- Three benchmark tasks with increasing difficulty
- Deterministic baseline inference script
- Dockerized for reproducible deployment

---

## 🛠 Tech Stack

- **Python 3.10**
- **FastAPI**
- **Uvicorn**
- **Pydantic**
- **Pytest**
- **Docker**

---

## 📂 Project Structure

```text
green_route_hackathon/
├── agents/             # Baseline agents / heuristics
├── frontend/           # Demo UI (optional presentation layer)
├── src/
│   ├── api/            # FastAPI endpoints and request/response schemas
│   └── core/           # Environment logic, physics, entities, graders
├── tests/              # Unit tests
├── Dockerfile          # Docker container config
├── inference.py        # Baseline benchmark runner
├── openenv.yaml        # OpenEnv manifest
├── README.md
└── requirements.txt
```

---

# 🧠 Environment Design

The environment models a **small urban delivery system** where an agent must assign trucks to delivery orders while balancing:

- **Delivery success**
- **Battery usage**
- **Vehicle assignment feasibility**
- **Carbon emissions**
- **Operational efficiency**

The environment is **stateful**, meaning each action changes truck energy, order completion, world time, and emissions.

This makes the benchmark closer to a **real-world logistics optimization task** rather than a toy simulation.

---

# 🎮 Action Space

Each environment step takes a single delivery assignment action:

```json
{
  "truck_id": "T1",
  "target_order_id": "O1"
}
```

### Action Meaning

At every step, the agent chooses:

- **which truck** should be used
- **which order** should be delivered next

This makes the decision problem interpretable and practical for RL or heuristic agents.

---

# 👀 Observation Space

Each observation returned by the environment contains:

```json
{
  "trucks": [...],
  "available_orders": [...],
  "world_time": 0
}
```

### Observation Components

#### Trucks
Each truck contains:

- `id`
- `truck_type` (`electric` or `diesel`)
- `capacity`
- `energy_level`
- `co2_emitted`
- `current_location`

#### Available Orders
Each order contains:

- `id`
- `location`
- `weight`
- `deadline`
- `is_delivered`

#### Global Context

- `world_time`

This observation space gives the agent enough information to make meaningful route and fleet decisions.

---

# 🔌 API Endpoints

The environment is exposed as a **FastAPI service**.

## `POST /reset`

Resets the environment for a selected benchmark task.

### Example

```bash
curl -X POST "http://127.0.0.1:8000/reset?task_id=basic_delivery"
```

---

## `POST /step`

Executes one environment step.

### Example Request

```json
{
  "truck_id": "T1",
  "target_order_id": "O1"
}
```

### Returns

- next observation
- reward
- done flag
- info dictionary

---

## `GET /state`

Returns the current full environment state.

---

## `GET /grade`

Returns the normalized benchmark score in **[0,1]** for the current task.

### Example

```bash
curl "http://127.0.0.1:8000/grade?task_id=basic_delivery"
```

---

## `GET /health`

Health-check endpoint used for validation and deployment checks.

---

# 🧪 Benchmark Tasks

This environment contains **three benchmark tasks** with increasing difficulty.

---

## 1) `basic_delivery` (Easy)

### Objective
Deliver a single nearby package successfully.

### Characteristics

- 1 order
- low weight
- easy deadline
- very clear best move

### Expected Outcome
A reasonable baseline agent should solve this almost perfectly.

---

## 2) `fleet_balancing` (Medium)

### Objective
Deliver multiple packages while making better truck-order assignments.

### Characteristics

- 2 orders
- moderate distances
- mixed weights
- battery tradeoffs begin to matter

### Expected Outcome
A naive policy may only partially succeed, while better planning improves score.

---

## 3) `carbon_challenge` (Hard)

### Objective
Maximize delivery success while minimizing carbon emissions and avoiding stranded trucks.

### Characteristics

- 3 orders
- heavier packages
- larger travel distances
- stronger electric vs diesel tradeoffs

### Expected Outcome
Greedy or careless agents often fail or incur avoidable penalties.

---

# 🧮 Reward Design

The environment provides **step-level reward signals**, not just sparse end-of-episode rewards.

## Positive Reward Signals

- successful delivery
- lower-carbon delivery behavior
- completing deliveries efficiently

## Negative Reward Signals

- invalid actions
- truck stranding
- inefficient delivery decisions
- failure to complete orders

This gives agents useful learning signal across the full trajectory.

---

# 📊 Grading & Evaluation

Each task has a corresponding grader that returns a score in:

```text
0.0 → 1.0
```

## Scoring Principles

- **basic_delivery** → binary success-based grading
- **fleet_balancing** → partial credit based on delivery completion
- **carbon_challenge** → balances delivery success and carbon efficiency

This allows deterministic and reproducible evaluation across different agents.

---

# ✅ Pre-Submission Validation

To verify that the environment is fully functional before submission, run:

```bash
python validate.py
```
---

# 🤖 Baseline Inference

The project includes a deterministic baseline runner:

```bash
python inference.py
```

This script automatically evaluates all 3 tasks and prints structured logs in the required format:

```text
[START] ...
[STEP] ...
[END] ...
```

The baseline uses a simple heuristic policy that:

- prioritizes available orders
- prefers electric trucks when feasible
- falls back to diesel when needed

---

## Example Baseline Behavior

| Task | Typical Result |
|------|----------------|
| `basic_delivery` | High / near-perfect |
| `fleet_balancing` | Partial success |
| `carbon_challenge` | Lower score / harder challenge |

This demonstrates that task difficulty scales meaningfully across the benchmark.

---

# 🚀 Local Setup

## 1. Create a virtual environment

```bash
python -m venv .venv
```

## 2. Activate it

### Windows (PowerShell)

```bash
.venv\Scripts\Activate
```

### macOS / Linux

```bash
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Run the API

```bash
uvicorn src.api.app:app --reload
```

## 5. Open Swagger Docs

```text
http://127.0.0.1:8000/docs
```

---

# 🐳 Docker Usage

## Build the Docker image

```bash
docker build -t green-route-env .
```

## Run the container

```bash
docker run -p 8000:8000 green-route-env
```

Then open:

```text
http://127.0.0.1:8000/docs
```

---

# 🌐 Deployment

This environment is designed to be deployed as a FastAPI service using Docker.

For hackathon submission, the environment can be hosted on platforms such as **Hugging Face Spaces** or other container-friendly deployment services.

Once deployed, the same OpenEnv endpoints remain available:

- `/reset`
- `/step`
- `/state`
- `/grade`
- `/health`

---

# 🖥 Optional Frontend Dashboard

A lightweight frontend dashboard is included for manual testing and demo purposes.  
It allows users to:

- select benchmark tasks
- reset the environment
- execute actions manually
- inspect truck and order state
- view task grades

This is not required for agent evaluation, but helps visualize environment behavior.

---

# 📌 Evaluation Summary

This environment supports both reinforcement learning and rule-based agents, though no training loop is enforced.
This project is designed to satisfy the main OpenEnv benchmark expectations:

- Real-world utility
- Multiple benchmark tasks
- Task-specific graders
- Meaningful reward shaping
- Deterministic baseline reproducibility
- API-first environment interaction
- Dockerized deployment

---

# 👩‍💻 Author / Submission Context

Created as part of the **Meta x PyTorch OpenEnv Hackathon**.

### Submission Focus

- Sustainable logistics
- Real-world AI benchmarking
- Agent decision-making under operational constraints
- Carbon-aware fleet optimization

---

