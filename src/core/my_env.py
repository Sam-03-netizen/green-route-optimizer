from typing import List, Optional, Tuple
from pydantic import BaseModel
from src.core.entities import Truck, Order
from src.core.physics import calculate_distance, calculate_energy_drain, calculate_co2


class Observation(BaseModel):
    trucks: List[dict]
    available_orders: List[dict]
    world_time: int


class Action(BaseModel):
    truck_id: str
    target_order_id: str


class GreenLogisticsEnv:
    def __init__(self, trucks: List[Truck], orders: List[Order]):
        self.all_trucks = trucks
        self.all_orders = orders
        self.world_time = 0
        self.done = False

    def reset(self, orders: Optional[List[Order]] = None) -> Observation:
        print("🔥 RESET FUNCTION CALLED WITH orders =", orders)

        if orders is not None:
            self.all_orders = orders

        for truck in self.all_trucks:
            truck.energy_level = 100.0
            truck.co2_emitted = 0.0
            truck.current_location = (0, 0)

        for order in self.all_orders:
            order.is_delivered = False

        self.world_time = 0
        self.done = False

        return self._get_observation()

    def step(self, action: Action) -> Tuple[Observation, float, bool, dict]:
        if self.done:
            return self._get_observation(), 0.0, True, {"error": "Env already done"}

        truck = next((t for t in self.all_trucks if t.id == action.truck_id), None)
        order = next((o for o in self.all_orders if o.id == action.target_order_id), None)

        if not truck or not order or order.is_delivered:
            return self._get_observation(), -5.0, False, {"error": "Invalid action"}

        dist = calculate_distance(truck.current_location, order.location)
        drain = calculate_energy_drain(dist, order.weight, truck.truck_type)

        if truck.energy_level < drain:
            truck.energy_level = 0
            self.done = True
            return self._get_observation(), -50.0, True, {"reason": "Truck stranded"}

        truck.energy_level -= drain
        co2_step = calculate_co2(dist, truck.truck_type)
        truck.co2_emitted += co2_step
        self.world_time += int(dist)
        truck.current_location = order.location

        step_reward = 10.0 - (co2_step * 0.1) if self.world_time <= order.deadline else -2.0
        if step_reward > 0:
            order.is_delivered = True

        if all(o.is_delivered for o in self.all_orders):
            self.done = True

        return self._get_observation(), step_reward, self.done, {}

    def _truck_to_dict(self, truck: Truck) -> dict:
        return {
            "id": truck.id,
            "truck_type": truck.truck_type,
            "capacity": truck.capacity,
            "energy_level": truck.energy_level,
            "co2_emitted": truck.co2_emitted,
            "current_location": list(truck.current_location),
        }

    def _order_to_dict(self, order: Order) -> dict:
        return {
            "id": order.id,
            "location": list(order.location),
            "weight": order.weight,
            "deadline": order.deadline,
            "is_delivered": order.is_delivered,
        }

    def _get_observation(self) -> Observation:
        return Observation(
            trucks=[self._truck_to_dict(t) for t in self.all_trucks],
            available_orders=[self._order_to_dict(o) for o in self.all_orders if not o.is_delivered],
            world_time=self.world_time
        )

    def state(self) -> dict:
        return {
            "trucks": [self._truck_to_dict(t) for t in self.all_trucks],
            "orders": [self._order_to_dict(o) for o in self.all_orders],
            "world_time": self.world_time,
            "done": self.done
        }