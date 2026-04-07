import requests

API_URL = "http://127.0.0.1:8000/simulate"

# Mock order metadata (same as backend for now)
orders = {
    "O1": {"weight": 10, "deadline": 50},
    "O2": {"weight": 5, "deadline": 100},
    "O3": {"weight": 20, "deadline": 150},
}

def generate_manifest():
    """
    Simple heuristic:
    - Prioritize electric truck (T1) for lighter / earlier orders
    - Put heavier remaining orders into diesel truck (T2)
    """
    t1 = []
    t2 = []

    for order_id, info in orders.items():
        if info["weight"] <= 10 and info["deadline"] <= 100:
            t1.append(order_id)
        else:
            t2.append(order_id)

    return {
        "manifest": {
            "T1": t1,
            "T2": t2
        }
    }

def run_agent():
    payload = generate_manifest()
    print("Generated Manifest:", payload)

    response = requests.post(API_URL, json=payload)

    if response.status_code == 200:
        print("Simulation Result:")
        print(response.json())
    else:
        print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    run_agent()