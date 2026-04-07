import requests
import subprocess
import sys

BASE_URL = "http://127.0.0.1:8000"

TASKS = [
    "basic_delivery",
    "fleet_balancing",
    "carbon_challenge"
]


def check_health():
    print("\n[CHECK] /health")
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200, f"/health failed: {r.status_code}"
    print("[PASS] Health endpoint works")


def check_reset(task_id):
    print(f"\n[CHECK] /reset for task={task_id}")
    r = requests.post(f"{BASE_URL}/reset", params={"task_id": task_id})
    assert r.status_code == 200, f"/reset failed for {task_id}: {r.status_code}"
    data = r.json()
    assert "trucks" in data, "Reset response missing 'trucks'"
    assert "available_orders" in data, "Reset response missing 'available_orders'"
    print(f"[PASS] Reset works for {task_id}")


def check_state():
    print("\n[CHECK] /state")
    r = requests.get(f"{BASE_URL}/state")
    assert r.status_code == 200, f"/state failed: {r.status_code}"
    data = r.json()
    assert "trucks" in data, "State missing 'trucks'"
    assert "orders" in data, "State missing 'orders'"
    assert "world_time" in data, "State missing 'world_time'"
    assert "done" in data, "State missing 'done'"
    print("[PASS] State endpoint works")


def check_step():
    print("\n[CHECK] /step")
    # Reset first so step is valid
    requests.post(f"{BASE_URL}/reset", params={"task_id": "basic_delivery"})

    payload = {
        "truck_id": "T1",
        "target_order_id": "O1"
    }

    r = requests.post(f"{BASE_URL}/step", json=payload)
    assert r.status_code == 200, f"/step failed: {r.status_code}"
    data = r.json()
    assert "observation" in data, "Step response missing 'observation'"
    assert "reward" in data, "Step response missing 'reward'"
    assert "done" in data, "Step response missing 'done'"
    assert "info" in data, "Step response missing 'info'"
    print("[PASS] Step endpoint works")


def check_grade(task_id):
    print(f"\n[CHECK] /grade for task={task_id}")
    requests.post(f"{BASE_URL}/reset", params={"task_id": task_id})

    r = requests.get(f"{BASE_URL}/grade", params={"task_id": task_id})
    assert r.status_code == 200, f"/grade failed for {task_id}: {r.status_code}"
    data = r.json()

    assert "score" in data, "Grade response missing 'score'"
    score = data["score"]
    assert 0.0 <= score <= 1.0, f"Score out of range for {task_id}: {score}"
    print(f"[PASS] Grade works for {task_id} (score={score})")


def check_inference():
    print("\n[CHECK] inference.py")
    result = subprocess.run(
        [sys.executable, "inference.py"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, "inference.py crashed"
    output = result.stdout

    assert "[START]" in output, "Inference missing [START] logs"
    assert "[STEP]" in output, "Inference missing [STEP] logs"
    assert "[END]" in output, "Inference missing [END] logs"

    print("[PASS] inference.py runs correctly")
    print("\n--- inference.py output preview ---")
    print(output[:1000])


def main():
    print("====================================")
    print(" GREEN ROUTE PRE-VALIDATION CHECK ")
    print("====================================")

    check_health()

    for task in TASKS:
        check_reset(task)

    check_state()
    check_step()

    for task in TASKS:
        check_grade(task)

    check_inference()

    print("\n====================================")
    print(" ALL VALIDATION CHECKS PASSED ")
    print("====================================")


if __name__ == "__main__":
    main()