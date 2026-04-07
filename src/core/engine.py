from src.core.entities import Truck, Order
from src.core.physics import calculate_distance, calculate_energy_drain, calculate_co2
from src.core.reward_system import compute_reward

class LogisticsEngine:
    def __init__(self, trucks, orders):
        self.trucks = trucks
        self.orders = orders
        self.world_time = 0  # Clock starts at 0

    def run_manifest(self, manifest):
        # ✅ RESET STATE
        for truck in self.trucks:
            truck.energy_level = 100.0
            truck.co2_emitted = 0.0
            truck.current_location = (0, 0)

        for order in self.orders:
            order.is_delivered = False

        total_delivered_count = 0
        total_pollution = 0
        stranded_trucks = 0

        for truck in self.trucks:
            # Use manifest.get to fetch orders for THIS truck, or empty list
            route_ids = manifest.get(truck.id, [])
            current_pos = (0, 0)
            truck_time = 0
            is_truck_failed = False # Local flag to prevent double-counting failures

            for order_id in route_ids:
                order = next((o for o in self.orders if o.id == order_id), None)
                if not order:
                    continue

                dist = calculate_distance(current_pos, order.location)
                drain = calculate_energy_drain(dist, order.weight, truck.truck_type)

                # Check if truck dies mid-delivery
                if truck.energy_level < drain:
                    stranded_trucks += 1
                    is_truck_failed = True
                    break 

                # Update truck status
                truck.energy_level -= drain
                truck.co2_emitted += calculate_co2(dist, truck.truck_type)
                truck_time += dist
                current_pos = order.location

                # ✅ FIXED: Only increment if this specific order hasn't been delivered yet
                if truck_time <= order.deadline and not order.is_delivered:
                    order.is_delivered = True
                    total_delivered_count += 1

            # Final Step: Return to Hub (Only if truck hasn't already failed)
            if not is_truck_failed:
                return_dist = calculate_distance(current_pos, (0, 0))
                return_drain = calculate_energy_drain(return_dist, 0, truck.truck_type)

                if truck.energy_level < return_drain:
                    stranded_trucks += 1
                else:
                    truck.energy_level -= return_drain
                    truck.co2_emitted += calculate_co2(return_dist, truck.truck_type)

            # Accumulate this truck's pollution to the total
            total_pollution += truck.co2_emitted

        # Calculate final reward based on unique deliveries and total pollution
        final_score = compute_reward(total_delivered_count, total_pollution, stranded_trucks)
        return final_score, total_delivered_count