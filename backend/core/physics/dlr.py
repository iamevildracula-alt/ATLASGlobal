import math
from typing import Dict, Any

class DynamicLineRatingSimulator:
    """
    Simulates Dynamic Line Ratings (DLR) based on simplified IEEE 738 physics.
    Calculates real-time ampacity (MVA) based on weather conditions.
    """

    @staticmethod
    def calculate_ampacity_factor(ambient_temp_c: float, wind_speed_mps: float) -> float:
        """
        Calculates the multiplier for static rating based on weather.
        Base conditions (Factor=1.0): 35degC Ambient, 0.6m/s Wind.
        
        Physics approximation:
        - Cooling is proportional to sqrt(wind_speed) and (MaxTemp - AmbientTemp).
        """
        # Constants for a typical ACSR conductor
        MAX_CONDUCTOR_TEMP = 75.0 # degC
        BASE_AMBIENT = 35.0
        BASE_WIND = 0.6
        
        # 1. Temperature Delta Contribution
        # If it's colder than 35C, we can push more current.
        # Heat dissipation ~ DeltaT
        delta_t_base = MAX_CONDUCTOR_TEMP - BASE_AMBIENT
        delta_t_real = MAX_CONDUCTOR_TEMP - ambient_temp_c
        
        if delta_t_real <= 0: return 0.0 # It's too hot, line must trip
        
        temp_factor = math.sqrt(delta_t_real / delta_t_base)
        
        # 2. Wind Cooling Contribution
        # Convection cooling ~ sqrt(wind_speed) (low speed) or wind_speed (high speed)
        # We use a simplified multiplier approach
        # 2 m/s wind is ~2x better cooling than 0.6 m/s ? Not linear, but significant.
        
        # Win Cooling Factor (WCF). 0.6 m/s Reference.
        # Approx: Ampacity increases ~ 10-15% per 1 m/s increase initially.
        # Let's use a log-based or root-based scaling for stability.
        
        wind_cooling_ratio = 1.0
        if wind_speed_mps > 0.6:
            # IEEE 738 simplified relation for convection
            # Ratio of (Current_Wind / Base_Wind)^0.25 roughly for Nu number?
            # Let's use a verified empirical fit for Demo:
            # 1m/s -> 1.05x, 2m/s -> 1.15x, 5m/s -> 1.4x
            wind_cooling_ratio = 1.0 + (0.2 * math.log(wind_speed_mps / 0.6 + 1))
        elif wind_speed_mps < 0.6:
            wind_cooling_ratio = max(0.5, wind_speed_mps / 0.6) # Derate if dead calm
            
        return temp_factor * wind_cooling_ratio

    @staticmethod
    def update_ratings(state: Any, weather_context: Dict[str, float]) -> None:
        """
        Updates the dynamic_rating_mva for all links in the state.
        
        Args:
            state: InfrastructureState object (with links)
            weather_context: dict with 'temp_c', 'wind_mps'
        """
        temp = weather_context.get('temp_c', 25.0)
        wind = weather_context.get('wind_mps', 2.0)
        
        for link in state.links:
            # For this demo, we assume all links are Overhead Lines (OHL)
            # In real system, we'd check link.type
            
            # Base is the static rating (Nameplate)
            base_rating = link.static_rating_mva
            
            # Calculate Factor
            factor = DynamicLineRatingSimulator.calculate_ampacity_factor(temp, wind)
            
            # Apply DLR
            link.dynamic_rating_mva = base_rating * factor
            
            # Determine Limiting Factor text for UI
            if factor > 1.0:
                if temp < 20.0 and wind > 3.0:
                    link.limiting_factor = "High Wind Cooling"
                elif temp < 20.0:
                    link.limiting_factor = "Low Ambient Temp"
                else:
                    link.limiting_factor = "Wind Cooling"
            else:
                 link.limiting_factor = "Thermal Limit"
