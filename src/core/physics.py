import math

def calculate_distance(pos1, pos2):
    # Standard math to find distance between two points on a grid
    return math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)

def calculate_energy_drain(distance, weight, truck_type):
    # Base drain is 0.5% per unit of distance
    # We add 0.1% for every unit of weight
    drain = distance * (0.5 + (weight * 0.1))
    return drain

def calculate_co2(distance, truck_type):
    # Electric is clean (0), Diesel emits 5 units per distance
    if truck_type == "diesel":
        return distance * 5.0
    return 0.0