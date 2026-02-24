import os
import random
import time
from datetime import datetime
from typing import Optional
import aiohttp
from backend.models.schemas import WeatherData, MarketPrice

class ExternalDataBridge:
    def __init__(self):
        self.weather_api_key = os.getenv("OPENWEATHER_API_KEY")
        self.market_api_key = os.getenv("MARKET_DATA_API_KEY") # e.g., AlphaVantage or EIA
        
    async def get_current_weather(self, lat: float = 28.6139, lon: float = 77.2090) -> WeatherData:
        """
        Fetches live weather or simulates high-fidelity solar/wind conditions.
        """
        if self.weather_api_key:
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.weather_api_key}&units=metric"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return WeatherData(
                                timestamp=datetime.utcnow().isoformat(),
                                temperature=data['main']['temp'],
                                wind_speed=data['wind']['speed'],
                                irradiance=800.0 if "clear" in data['weather'][0]['description'].lower() else 200.0,
                                condition=data['weather'][0]['main']
                            )
            except Exception as e:
                print(f"Weather API Error: {e}. Falling back to simulator.")

        return self._simulate_weather()

    async def get_real_carbon_intensity(self) -> float:
        """ Fetches real-time carbon intensity (gCO2/kWh) from UK National Grid. """
        try:
            url = "https://api.carbonintensity.org.uk/intensity"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return float(data['data'][0]['intensity']['actual'] or data['data'][0]['intensity']['forecast'])
        except Exception as e:
            print(f"Carbon API Error: {e}")
        return 35.0 + random.uniform(-5, 5)

    async def get_real_grid_demand(self) -> float:
        """ Fetches real-time grid demand (MW) from National Grid ESO. """
        try:
            # Resource: Real-time outturn
            url = "https://api.nationalgridesto.com/api/3/action/datastore_search?resource_id=88313a7e-132d-40bb-91a5-83c92e59e4b6&limit=1"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        record = data['result']['records'][0]
                        # Return MW (scaled for demo if needed, but we wanted real data)
                        return float(record['value'])
        except Exception as e:
            print(f"Demand API Error: {e}")
        return 450.0 + random.uniform(-20, 20)

    async def get_market_price(self) -> MarketPrice:
        """
        Fetches live market clearing price (MCP) or simulates price volatility.
        """
        if self.market_api_key:
            # Placeholder for real market integration
            pass

        return self._simulate_market()

    def _simulate_weather(self) -> WeatherData:
        # Time-based simulation (Daily solar cycle)
        hour = datetime.now().hour
        is_day = 6 <= hour <= 18
        base_irradiance = 850 if is_day else 0
        noise = random.uniform(-50, 50) if is_day else 0
        
        return WeatherData(
            timestamp=datetime.utcnow().isoformat(),
            temperature=25.0 + random.uniform(-5, 5),
            wind_speed=5.0 + random.uniform(0, 10),
            irradiance=max(0, base_irradiance + noise),
            condition="Clear" if is_day else "Night"
        )

    def _simulate_market(self) -> MarketPrice:
        # Volatility simulation
        hour = datetime.now().hour
        is_peak = 10 <= hour <= 14 or 18 <= hour <= 21
        base_price = 75.0 if is_peak else 45.0
        
        return MarketPrice(
            timestamp=datetime.utcnow().isoformat(),
            price_per_mwh=base_price + random.uniform(-10, 20),
            currency="USD"
        )

# Global bridge instance
context_bridge = ExternalDataBridge()
