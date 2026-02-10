from ..models.schemas import InfrastructureState, EnergySource, EnergyType, EnergyDemand
from typing import List

class MockDataService:
    @staticmethod
    def get_default_state() -> InfrastructureState:
        return InfrastructureState(
            sources=[
                EnergySource(type=EnergyType.SOLAR, capacity=200.0, cost_per_mwh=40.0, carbon_intensity=10.0),
                EnergySource(type=EnergyType.WIND, capacity=150.0, cost_per_mwh=50.0, carbon_intensity=15.0),
                EnergySource(type=EnergyType.GRID, capacity=500.0, cost_per_mwh=120.0, carbon_intensity=400.0),
                EnergySource(type=EnergyType.BATTERY, capacity=100.0, cost_per_mwh=10.0, carbon_intensity=0.0),
                EnergySource(type=EnergyType.NUCLEAR, capacity=100.0, cost_per_mwh=80.0, carbon_intensity=5.0),
            ],
            storage_capacity_mwh=500.0,
            current_storage_mwh=250.0,
            carbon_limit=1000.0
        )

    @staticmethod
    def get_hourly_demand() -> List[EnergyDemand]:
        return [EnergyDemand(hour=i, demand_mw=300 + (i * 10 if i < 12 else (24-i) * 10)) for i in range(24)]
