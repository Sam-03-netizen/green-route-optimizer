def grade_basic_delivery(delivered_count, total_orders, total_co2, stranded):
    """
    Easy task:
    Full score only if the single package is delivered and no truck is stranded.
    """
    if stranded > 0:
        return 0.0
    return 1.0 if delivered_count >= 1 else 0.0


def grade_fleet_optimization(delivered_count, total_orders, total_co2, stranded):
    """
    Medium task:
    Partial credit for deliveries, with a penalty if any truck gets stranded.
    """
    if total_orders == 0:
        return 0.0

    base_score = delivered_count / total_orders
    penalty = 0.2 if stranded > 0 else 0.0
    return round(max(0.0, min(base_score - penalty, 1.0)), 3)


def grade_carbon_challenge(delivered_count, total_orders, total_co2, stranded):
    """
    Hard task:
    Rewards delivery completion, but penalizes high CO2 output.
    """
    if total_orders == 0:
        return 0.0

    delivery_ratio = delivered_count / total_orders
    co2_penalty = min(0.5, total_co2 / 1000.0)
    stranded_penalty = 0.2 if stranded > 0 else 0.0

    score = delivery_ratio - co2_penalty - stranded_penalty
    return round(max(0.0, min(score, 1.0)), 3)


def extract_metrics_from_state(state: dict):
    """
    Converts env.state() into the values needed by the graders.
    """
    orders = state.get("orders", [])
    trucks = state.get("trucks", [])

    total_orders = len(orders)
    delivered_count = sum(1 for o in orders if o.get("is_delivered"))
    total_co2 = sum(t.get("co2_emitted", 0.0) for t in trucks)

    # Define stranded truck as one with zero or less energy
    stranded = sum(1 for t in trucks if t.get("energy_level", 0) <= 0)

    return delivered_count, total_orders, total_co2, stranded


def grade_task(task_id: str, state: dict) -> float:
    """
    Main task dispatcher.
    Returns a normalized score in [0,1].
    """
    delivered_count, total_orders, total_co2, stranded = extract_metrics_from_state(state)

    if task_id == "basic_delivery":
        return grade_basic_delivery(delivered_count, total_orders, total_co2, stranded)

    elif task_id == "fleet_balancing":
        return grade_fleet_optimization(delivered_count, total_orders, total_co2, stranded)

    elif task_id == "carbon_challenge":
        return grade_carbon_challenge(delivered_count, total_orders, total_co2, stranded)

    return 0.0