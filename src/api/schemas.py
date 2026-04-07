from pydantic import BaseModel
from typing import List, Dict

class RouteManifest(BaseModel):
    # This is what the AI sends us
    # Example: {"truck_01": ["order_1", "order_2"]}
    manifest: Dict[str, List[str]]

class SimulationResult(BaseModel):
    # This is what we send back to the AI
    score: float
    delivered_count: int
    total_co2: float
    status: str
    efficiency_rating: str
    sustainability_note: str