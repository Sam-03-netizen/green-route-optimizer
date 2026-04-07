import pytest
from src.core.entities import Truck, Order
from src.core.engine import LogisticsEngine


def test_electric_vs_diesel_co2():
    # Setup
    t1 = Truck(id="T1", truck_type="electric", capacity=100)
    t2 = Truck(id="T2", truck_type="diesel", capacity=100)

    order = Order(id="O1", location=(10, 0), weight=10, deadline=100)

    # Run electric scenario
    engine = LogisticsEngine(trucks=[t1, t2], orders=[order])
    engine.run_manifest({"T1": ["O1"], "T2": []})
    electric_co2 = t1.co2_emitted

    # Reset fresh objects for diesel test (IMPORTANT)
    t1 = Truck(id="T1", truck_type="electric", capacity=100)
    t2 = Truck(id="T2", truck_type="diesel", capacity=100)
    order = Order(id="O1", location=(10, 0), weight=10, deadline=100)

    engine = LogisticsEngine(trucks=[t1, t2], orders=[order])
    engine.run_manifest({"T1": [], "T2": ["O1"]})
    diesel_co2 = t2.co2_emitted

    # Assertions
    assert electric_co2 == 0
    assert diesel_co2 > 0


def test_battery_depletion():
    t1 = Truck(id="T1", truck_type="electric", capacity=100)
    order = Order(id="O1", location=(50, 50), weight=50, deadline=100)

    engine = LogisticsEngine(trucks=[t1], orders=[order])
    engine.run_manifest({"T1": ["O1"]})

    assert t1.energy_level <= 100