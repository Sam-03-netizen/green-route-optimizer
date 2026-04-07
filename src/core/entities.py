from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class Order:
    id: str
    location: Tuple[int, int]  # (x, y) coordinates
    weight: float               # Heavier packages = more battery drain
    deadline: int               # Minutes from start (e.g., 60)
    is_delivered: bool = False

@dataclass
class Truck:
    id: str
    truck_type: str             # "electric" or "diesel"
    capacity: float             # Max weight it can carry
    energy_level: float = 100.0 # Percentage (0 to 100)
    current_location: Tuple[int, int] = (0, 0) # All start at the Hub
    co2_emitted: float = 0.0    # Tracks pollution for this truck