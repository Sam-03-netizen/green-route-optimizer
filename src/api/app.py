from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.schemas import RouteManifest, SimulationResult
from src.core.entities import Truck, Order
from src.core.engine import LogisticsEngine
from src.core.my_env import GreenLogisticsEnv, Action
from src.core.graders import grade_task

app = FastAPI(title="Green Route Logistics Optimizer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. DEFINE TASK DATA ---

# Shared fleet
mock_trucks = [
    Truck(id="T1", truck_type="electric", capacity=100),
    Truck(id="T2", truck_type="diesel", capacity=200)
]

# TASK 1 — EASY
basic_delivery_orders = [
    Order(id="O1", location=(10, 20), weight=10, deadline=50)
]

# TASK 2 — MEDIUM
fleet_balancing_orders = [
    Order(id="O1", location=(15, 10), weight=10, deadline=40),
    Order(id="O2", location=(35, 25), weight=25, deadline=80)
]

# TASK 3 — HARD
carbon_challenge_orders = [
    Order(id="O1", location=(10, 20), weight=10, deadline=50),
    Order(id="O2", location=(80, 80), weight=40, deadline=100),
    Order(id="O3", location=(50, 10), weight=50, deadline=150)
]

# Task registry
TASKS = {
    "basic_delivery": basic_delivery_orders,
    "fleet_balancing": fleet_balancing_orders,
    "carbon_challenge": carbon_challenge_orders,
}

# Initialize environment with default task
env = GreenLogisticsEnv(trucks=mock_trucks, orders=basic_delivery_orders)

# --- 2. STANDARD ENDPOINTS (For React Frontend) ---

@app.get("/")
def home():
    return {"message": "Green Route Optimizer API is running! Go to /docs to test."}

@app.post("/simulate", response_model=SimulationResult)
def run_simulation(data: RouteManifest):
    """
    React/frontend batch simulation.
    Uses the hardest task as the default simulation benchmark.
    """
    engine = LogisticsEngine(trucks=mock_trucks, orders=carbon_challenge_orders)
    score, delivered = engine.run_manifest(data.manifest)

    total_co2 = round(sum(t.co2_emitted for t in mock_trucks), 2)

    if score >= 0:
        efficiency_rating = "High"
    elif score > -200:
        efficiency_rating = "Moderate"
    else:
        efficiency_rating = "Poor"

    return SimulationResult(
        score=round(score, 2),
        delivered_count=delivered,
        total_co2=total_co2,
        status="Success",
        efficiency_rating=efficiency_rating,
        sustainability_note="Simulation complete."
    )

# --- 3. OPENENV AGENTIC ENDPOINTS (For Hackathon Judges) ---

@app.post("/reset")
def reset_env(task_id: str = "basic_delivery"):
    """Resets the environment for a specific benchmark task."""
    current_orders = TASKS.get(task_id, basic_delivery_orders)
    obs = env.reset(orders=current_orders)
    return obs

@app.post("/step")
def step_env(action: Action):
    """Executes a single step for the RL Agent."""
    obs, reward, done, info = env.step(action)
    return {
        "observation": obs,
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/state")
def get_state():
    return env.state()

@app.get("/grade")
def grade_env(task_id: str = "basic_delivery"):
    """
    Returns normalized benchmark score [0,1] for the current state.
    """
    state = env.state()
    score = grade_task(task_id, state)

    return {
        "task_id": task_id,
        "score": round(score, 3),
        "state_summary": {
            "delivered": sum(1 for o in state["orders"] if o["is_delivered"]),
            "total_orders": len(state["orders"]),
            "total_co2": round(sum(t["co2_emitted"] for t in state["trucks"]), 2)
        }
    }

@app.get("/health")
def health_check():
    return {"status": "online", "environment": "OpenEnv"}


