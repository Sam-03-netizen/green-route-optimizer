def compute_reward(on_time_deliveries, total_co2, stranded_trucks):
    # +10 points for every success
    reward = on_time_deliveries * 10.0
    
    # -1 point for every unit of pollution
    reward -= total_co2
    
    # -50 points if a truck runs out of energy (Massive failure!)
    reward -= (stranded_trucks * 50.0)
    
    return reward