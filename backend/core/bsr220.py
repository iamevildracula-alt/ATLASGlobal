from pydantic import BaseModel
from typing import Dict, Any
import math

class BSR220State(BaseModel):
    # Core Telemetry
    core_temperature: float = 285.0  # Celsius
    coolant_pressure: float = 15.5  # MPa
    control_rod_insertion: float = 0.5  # 0.0 (removed) to 1.0 (fully inserted)
    reactivity_index: float = 0.0   # pcm (units of reactivity)
    power_output_mw: float = 0.0
    
    # Safety Limits
    MAX_TEMP: float = 650.0 # C
    MAX_PRESSURE: float = 18.0 # MPa
    TRIP_TEMP: float = 700.0 # Emergency shutdown threshold

class BSR220Controller:
    """
    Specialized Safety Controller for the BSR-220 SMR.
    Ensures that power dispatch requests do not violate physical safety envelopes.
    """
    
    @staticmethod
    def calculate_thermal_margin(state: BSR220State) -> float:
        """Returns the safety margin before a thermal trip occurs (0.0 to 1.0)"""
        if state.core_temperature >= state.TRIP_TEMP:
            return 0.0
        return (state.TRIP_TEMP - state.core_temperature) / (state.TRIP_TEMP - 285.0)

    @staticmethod
    def simulate_step(state: BSR220State, target_mw: float, dt_seconds: float = 1.0) -> BSR220State:
        """
        Simulates one time-step of reactor dynamics based on a power request.
        Implements a simplified thermal-hydraulic feedback loop.
        """
        new_state = state.copy()
        
        # 1. Neutronics: Control rod adjustment toward target power
        # Simple proportional control
        target_insertion = 1.0 - (target_mw / 220.0) # 0.0 rods = 220MW, 1.0 rods = 0MW
        insertion_delta = (target_insertion - state.control_rod_insertion) * 0.1
        new_state.control_rod_insertion = max(0.0, min(1.0, state.control_rod_insertion + insertion_delta))
        
        # 2. Power Gen: Power is inversely proportional to rod insertion
        new_state.power_output_mw = 220.0 * (1.0 - new_state.control_rod_insertion)
        
        # 3. Thermal Dynamics: Temp increases with power, decreases with coolant flow (simulated as constant)
        # Heat added = power, Heat removed = (temp - ambient) * cooling_factor
        heat_factor = 0.05
        cooling_factor = 0.02
        temp_delta = (new_state.power_output_mw * heat_factor) - ((new_state.core_temperature - 285.0) * cooling_factor)
        new_state.core_temperature += temp_delta * dt_seconds
        
        # 4. Pressure Dynamics: Ideal gas law approximation (Simplified)
        pressure_factor = 0.01
        new_state.coolant_pressure = 15.5 + (new_state.core_temperature - 285.0) * pressure_factor
        
        # 5. Safety Override: Automated SCRAM (Safety Control Rod Axe Man)
        if new_state.core_temperature > state.TRIP_TEMP:
            new_state.control_rod_insertion = 1.0 # Emergency drop
            new_state.power_output_mw = 0.0
            
        return new_state

    @staticmethod
    def get_dispatch_constraints(state: BSR220State) -> Dict[str, float]:
        """Returns physics-based limits for the optimization engine"""
        margin = BSR220Controller.calculate_thermal_margin(state)
        
        # If margin is low, aggressively cap maximum allowed power
        safe_max_mw = 220.0 * min(1.0, margin * 2.0)
        
        return {
            "min_mw": 50.0, # SMRs have a minimum 'keep-warm' power
            "max_mw": float(safe_max_mw),
            "ramp_rate_mw_min": 5.0 # Nuclear ramps are slow
        }
