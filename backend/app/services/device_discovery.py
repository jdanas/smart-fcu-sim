import random
import asyncio
from datetime import datetime
from typing import Optional, Callable, Awaitable
from app.schemas import DeviceCreate, DeviceResponse


class DeviceDiscoverySimulator:
    """Simulates plug-and-play device discovery events."""

    DEVICE_TEMPLATES = [
        {
            "prefix": "sensor",
            "type": "sensor",
            "names": [
                "Temperature Sensor",
                "Humidity Sensor",
                "Multi Sensor",
                "Air Quality Sensor",
            ],
        },
        {
            "prefix": "fcu",
            "type": "fcu",
            "names": ["Fan Coil Unit", "Mini FCU", "Ceiling FCU"],
        },
    ]

    ZONES = ["server-room", "open-office"]

    def __init__(self):
        self._device_counter = 0
        self._running = False
        self._callback: Optional[Callable[[dict], Awaitable[None]]] = None

    def _generate_device_id(self, device_type: str, zone_id: str) -> str:
        """Generate a unique device ID."""
        self._device_counter += 1
        zone_prefix = "sr" if zone_id == "server-room" else "of"
        return f"{device_type}-{zone_prefix}-{self._device_counter:02d}"

    def _generate_random_device(self) -> DeviceCreate:
        """Generate a random new device."""
        template = random.choice(self.DEVICE_TEMPLATES)
        zone_id = random.choice(self.ZONES)
        device_id = self._generate_device_id(template["prefix"], zone_id)
        name = f"{random.choice(template['names'])} {self._device_counter}"

        return DeviceCreate(
            id=device_id,
            name=name,
            type=template["type"],
            zone_id=zone_id,
            status="syncing",
        )

    async def simulate_discovery_event(self) -> Optional[dict]:
        """
        Simulate a discovery event with probabilities:
        - 70%: No event
        - 20%: New device discovered
        - 10%: Existing device goes offline (handled separately)
        """
        roll = random.random()

        if roll > 0.3:  # 70% - no event
            return None

        if roll > 0.1:  # 20% - new device
            device = self._generate_random_device()
            return {
                "type": "device_discovered",
                "device": device.model_dump(),
                "timestamp": datetime.now().isoformat(),
            }

        # 10% - device status change (will be handled by the caller)
        return {
            "type": "device_status_change",
            "status": random.choice(["offline", "syncing"]),
            "timestamp": datetime.now().isoformat(),
        }

    async def start_discovery_loop(
        self, callback: Callable[[dict], Awaitable[None]], interval: float = 30.0
    ):
        """Start the background discovery simulation loop."""
        self._running = True
        self._callback = callback

        while self._running:
            await asyncio.sleep(interval + random.uniform(-5, 10))

            event = await self.simulate_discovery_event()
            if event and self._callback:
                await self._callback(event)

    def stop(self):
        """Stop the discovery loop."""
        self._running = False


# Global instance
discovery_simulator = DeviceDiscoverySimulator()
