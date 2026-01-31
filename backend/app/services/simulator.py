import random
import math
from datetime import datetime
from typing import Dict, Tuple


class MockDataGenerator:
    """Generates realistic mock sensor data for HVAC zones."""

    # Zone-specific profiles
    ZONE_PROFILES = {
        "server-room": {
            "base_temp": 18.0,
            "temp_variance": 0.3,
            "base_humidity": 45.0,
            "humidity_variance": 3.0,
            "power_base": 2.0,
            "power_variance": 0.5,
            "has_occupancy": False,
            "has_co2": False,
        },
        "open-office": {
            "base_temp": 23.0,
            "temp_variance": 0.8,
            "base_humidity": 55.0,
            "humidity_variance": 5.0,
            "power_base": 1.5,
            "power_variance": 0.3,
            "has_occupancy": True,
            "has_co2": True,
            "max_occupancy": 25,
        },
    }

    def __init__(self):
        self._temp_state: Dict[str, float] = {}
        self._humidity_state: Dict[str, float] = {}
        self._trend_direction: Dict[str, int] = {}

    def _get_time_factor(self) -> float:
        """Returns a factor based on time of day (simulates daily patterns)."""
        hour = datetime.now().hour
        # Peak heat around 2PM, cool in early morning
        return math.sin((hour - 6) * math.pi / 12) * 0.5

    def _get_occupancy_factor(self, zone_id: str) -> Tuple[int, float]:
        """Simulates occupancy patterns for office zones."""
        hour = datetime.now().hour
        day = datetime.now().weekday()

        # Weekend - minimal occupancy
        if day >= 5:
            occupancy = random.randint(0, 2)
            return occupancy, occupancy * 0.05

        # Business hours (8AM - 6PM)
        if 8 <= hour <= 18:
            # Peak at lunch time
            peak_factor = 1 - abs(hour - 13) / 5
            max_occ = self.ZONE_PROFILES.get(zone_id, {}).get("max_occupancy", 10)
            occupancy = int(max_occ * peak_factor * random.uniform(0.7, 1.0))
            return occupancy, occupancy * 0.1  # Body heat contribution

        return random.randint(0, 3), 0.0

    def generate_reading(self, zone_id: str, setpoint: float) -> dict:
        """Generate a realistic sensor reading for the given zone."""
        profile = self.ZONE_PROFILES.get(zone_id, self.ZONE_PROFILES["open-office"])

        # Initialize state if needed
        if zone_id not in self._temp_state:
            self._temp_state[zone_id] = profile["base_temp"]
            self._humidity_state[zone_id] = profile["base_humidity"]
            self._trend_direction[zone_id] = random.choice([-1, 1])

        # Temperature simulation with momentum
        time_factor = self._get_time_factor()

        # Add occupancy heat for office
        occupancy = None
        occupancy_heat = 0.0
        if profile.get("has_occupancy"):
            occupancy, occupancy_heat = self._get_occupancy_factor(zone_id)

        # Setpoint influence (HVAC trying to reach setpoint)
        current_temp = self._temp_state[zone_id]
        setpoint_pull = (setpoint - current_temp) * 0.05

        # Random walk with mean reversion
        noise = random.gauss(0, profile["temp_variance"] * 0.3)

        # Occasional trend changes
        if random.random() < 0.1:
            self._trend_direction[zone_id] *= -1

        trend = self._trend_direction[zone_id] * 0.02

        # Calculate new temperature
        new_temp = (
            current_temp
            + setpoint_pull
            + time_factor * 0.1
            + occupancy_heat
            + noise
            + trend
        )

        # Clamp to reasonable range
        new_temp = max(15.0, min(30.0, new_temp))
        self._temp_state[zone_id] = new_temp

        # Humidity simulation
        humidity_noise = random.gauss(0, profile["humidity_variance"] * 0.2)
        new_humidity = self._humidity_state[zone_id] + humidity_noise
        new_humidity = max(30.0, min(70.0, new_humidity))
        self._humidity_state[zone_id] = new_humidity

        # Build reading
        reading = {
            "temperature": round(new_temp, 2),
            "humidity": round(new_humidity, 1),
        }

        # Add power consumption (for FCU zones)
        power_base = profile.get("power_base", 1.5)
        power_variance = profile.get("power_variance", 0.3)
        # Power increases when temp is far from setpoint
        power_factor = 1 + abs(setpoint - new_temp) * 0.1
        reading["power_kw"] = round(
            power_base * power_factor + random.gauss(0, power_variance), 2
        )

        # Add CO2 for office
        if profile.get("has_co2"):
            base_co2 = 400  # Outdoor baseline
            co2 = base_co2 + (occupancy or 0) * 25 + random.gauss(0, 20)
            reading["co2_level"] = round(max(350, min(1200, co2)), 0)

        # Add occupancy
        if occupancy is not None:
            reading["occupancy"] = occupancy

        return reading


# Global instance
mock_generator = MockDataGenerator()
