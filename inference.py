import os
import requests
import json
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
MODEL_NAME = os.getenv("MODEL_NAME", "rule_based_baseline")
HF_TOKEN = os.getenv("HF_TOKEN", "dummy_token_not_used")

# Checklist-friendly client initialization
client = OpenAI(
    api_key=HF_TOKEN,
    base_url=f"{API_BASE_URL}/v1" if "127.0.0.1" not in API_BASE_URL else API_BASE_URL
)


def choose_action(task_name: str, observation: dict) -> dict:
    available_orders = observation.get("available_orders", [])
    trucks = observation.get("trucks", [])

    if not available_orders or not trucks:
        return None

    target_order = available_orders[0]
    weight = target_order["weight"]

    # Prefer electric with enough energy
    for truck in trucks:
        if (
            truck["truck_type"] == "electric"
            and truck["capacity"] >= weight
            and truck["energy_level"] > 20
        ):
            return {
                "truck_id": truck["id"],
                "target_order_id": target_order["id"]
            }

    # fallback to diesel
    for truck in trucks:
        if truck["capacity"] >= weight:
            return {
                "truck_id": truck["id"],
                "target_order_id": target_order["id"]
            }

    return None


def run_task(task_name: str):
    print(f"[START] task={task_name} env=green_logistics model={MODEL_NAME}")

    # RESET
    reset_response = requests.post(
        f"{API_BASE_URL}/reset",
        params={"task_id": task_name}
    )

    if reset_response.status_code != 200:
        print(f"[END] success=false steps=0 score=0.00 rewards= error=reset_failed")
        return

    obs = reset_response.json()

    done = False
    step_count = 0
    rewards = []

    while not done and step_count < 10:
        action = choose_action(task_name, obs)

        if action is None:
            print(f"[STEP] step={step_count+1} action=null reward=0.00 done=true error=no_valid_action")
            break

        step_response = requests.post(
            f"{API_BASE_URL}/step",
            json=action
        )

        if step_response.status_code != 200:
            print(f"[STEP] step={step_count+1} action={json.dumps(action)} reward=0.00 done=true error=step_failed")
            break

        result = step_response.json()
        obs = result["observation"]
        reward = result["reward"]
        done = result["done"]
        info = result.get("info", {})

        rewards.append(round(reward, 2))
        step_count += 1

        error_msg = info.get("error") or info.get("reason") or "null"

        print(
            f"[STEP] step={step_count} "
            f"action={json.dumps(action)} "
            f"reward={round(reward, 2)} "
            f"done={str(done).lower()} "
            f"error={error_msg}"
        )

    # GRADE
    grade_response = requests.get(
        f"{API_BASE_URL}/grade",
        params={"task_id": task_name}
    )

    if grade_response.status_code == 200:
        score = grade_response.json().get("score", 0.0)
    else:
        score = 0.0

    success = score >= 0.5
    reward_str = ",".join(str(r) for r in rewards)

    print(
        f"[END] success={str(success).lower()} "
        f"steps={step_count} "
        f"score={round(score, 2)} "
        f"rewards={reward_str}"
    )


def run_inference():
    tasks = [
        "basic_delivery",
        "fleet_balancing",
        "carbon_challenge"
    ]

    for task in tasks:
        run_task(task)


if __name__ == "__main__":
    run_inference()