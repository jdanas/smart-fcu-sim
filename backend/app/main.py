from contextlib import asynccontextmanager
import asyncio
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.config import get_settings
from app.database import init_db, async_session_maker
from app.models import Zone, Device, SensorReading, Prediction
from app.routers import (
    zones_router,
    devices_router,
    sensors_router,
    predictions_router,
    websocket_router,
)
from app.routers.chat import router as chat_router
from app.routers.websocket import (
    broadcast_sensor_reading,
    broadcast_device_event,
    broadcast_prediction,
)
from app.services import mock_generator, prediction_engine, discovery_simulator

settings = get_settings()

# Background task flags
background_tasks_running = False


async def seed_initial_data():
    """Seed initial zones and devices if database is empty."""
    async with async_session_maker() as db:
        # Check if zones exist
        result = await db.execute(select(Zone))
        zones = result.scalars().all()

        if not zones:
            # Create zones
            server_room = Zone(
                id="server-room",
                name="Server Room",
                setpoint=18.0,
                adaptive_mode=True,
            )
            open_office = Zone(
                id="open-office",
                name="Open Office",
                setpoint=23.0,
                adaptive_mode=True,
            )
            db.add(server_room)
            db.add(open_office)
            await db.commit()

            # Create initial devices
            devices = [
                Device(
                    id="fcu-sr-01",
                    name="FCU Server Room 1",
                    type="fcu",
                    zone_id="server-room",
                    status="online",
                    last_seen=datetime.now(),
                ),
                Device(
                    id="sensor-sr-01",
                    name="Temp/Humidity Sensor SR",
                    type="sensor",
                    zone_id="server-room",
                    status="online",
                    last_seen=datetime.now(),
                ),
                Device(
                    id="fcu-of-01",
                    name="FCU Open Office 1",
                    type="fcu",
                    zone_id="open-office",
                    status="online",
                    last_seen=datetime.now(),
                ),
                Device(
                    id="sensor-of-01",
                    name="Multi Sensor Office",
                    type="sensor",
                    zone_id="open-office",
                    status="online",
                    last_seen=datetime.now(),
                ),
            ]

            for device in devices:
                db.add(device)

            await db.commit()
            print("Database seeded with initial zones and devices")


async def sensor_data_loop():
    """Background task to generate and broadcast sensor data."""
    global background_tasks_running

    while background_tasks_running:
        try:
            async with async_session_maker() as db:
                # Get all zones with their setpoints
                result = await db.execute(select(Zone))
                zones = result.scalars().all()

                for zone in zones:
                    # Generate mock reading
                    reading_data = mock_generator.generate_reading(
                        zone.id, zone.setpoint
                    )

                    # Get sensor device for this zone
                    device_result = await db.execute(
                        select(Device)
                        .where(Device.zone_id == zone.id)
                        .where(Device.type == "sensor")
                        .limit(1)
                    )
                    sensor = device_result.scalar_one_or_none()

                    if sensor:
                        # Save reading to database
                        reading = SensorReading(
                            device_id=sensor.id,
                            zone_id=zone.id,
                            temperature=reading_data.get("temperature"),
                            humidity=reading_data.get("humidity"),
                            co2_level=reading_data.get("co2_level"),
                            power_kw=reading_data.get("power_kw"),
                            occupancy=reading_data.get("occupancy"),
                        )
                        db.add(reading)

                        # Update device last_seen
                        sensor.last_seen = datetime.now()

                        await db.commit()

                        # Broadcast to WebSocket clients
                        await broadcast_sensor_reading(
                            {
                                "type": "reading",
                                "zone_id": zone.id,
                                "device_id": sensor.id,
                                "data": reading_data,
                                "timestamp": datetime.now().isoformat(),
                            }
                        )

                        # Generate and broadcast prediction
                        await generate_and_broadcast_prediction(db, zone.id)

        except Exception as e:
            print(f"Error in sensor data loop: {e}")

        await asyncio.sleep(settings.sensor_update_interval)


async def generate_and_broadcast_prediction(db, zone_id: str):
    """Generate prediction and broadcast to clients."""
    from datetime import timedelta

    # Get recent readings
    cutoff = datetime.now() - timedelta(minutes=5)
    readings_query = (
        select(SensorReading)
        .where(SensorReading.zone_id == zone_id)
        .where(SensorReading.timestamp >= cutoff)
        .where(SensorReading.temperature.isnot(None))
        .order_by(SensorReading.timestamp)
    )

    result = await db.execute(readings_query)
    readings = result.scalars().all()

    temps = [r.temperature for r in readings if r.temperature is not None]

    if temps:
        current_temp = temps[-1]
        predicted_temp, confidence, trend = prediction_engine.predict(temps)

        # Save prediction
        prediction = Prediction(
            zone_id=zone_id,
            current_temp=current_temp,
            predicted_temp=predicted_temp,
            confidence=confidence,
            trend=trend,
        )
        db.add(prediction)
        await db.commit()

        # Broadcast prediction
        await broadcast_prediction(
            {
                "type": "prediction",
                "zone_id": zone_id,
                "current_temp": current_temp,
                "predicted_temp": predicted_temp,
                "confidence": confidence,
                "trend": trend,
                "timestamp": datetime.now().isoformat(),
            }
        )


async def device_discovery_callback(event: dict):
    """Handle device discovery events."""
    async with async_session_maker() as db:
        if event["type"] == "device_discovered":
            device_data = event["device"]

            # Create device in database
            device = Device(
                id=device_data["id"],
                name=device_data["name"],
                type=device_data["type"],
                zone_id=device_data["zone_id"],
                status="syncing",
            )
            db.add(device)
            await db.commit()

            # Broadcast discovery event
            await broadcast_device_event(event)

            # Simulate syncing -> online transition
            await asyncio.sleep(3)

            device.status = "online"
            device.last_seen = datetime.now()
            await db.commit()

            # Broadcast status change
            await broadcast_device_event(
                {
                    "type": "device_status",
                    "device_id": device.id,
                    "status": "online",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        elif event["type"] == "device_status_change":
            # Pick a random device to change status
            result = await db.execute(select(Device).where(Device.status == "online"))
            devices = result.scalars().all()

            if devices:
                import random

                device = random.choice(devices)
                new_status = event["status"]
                device.status = new_status
                await db.commit()

                await broadcast_device_event(
                    {
                        "type": "device_status",
                        "device_id": device.id,
                        "status": new_status,
                        "timestamp": datetime.now().isoformat(),
                    }
                )


async def start_background_tasks():
    """Start all background tasks."""
    global background_tasks_running
    background_tasks_running = True

    # Start sensor data generation
    asyncio.create_task(sensor_data_loop())

    # Start device discovery simulation
    asyncio.create_task(
        discovery_simulator.start_discovery_loop(
            device_discovery_callback, settings.discovery_check_interval
        )
    )


async def stop_background_tasks():
    """Stop all background tasks."""
    global background_tasks_running
    background_tasks_running = False
    discovery_simulator.stop()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    await init_db()
    await seed_initial_data()
    await start_background_tasks()
    print("Smart FCU Simulator started")

    yield

    # Shutdown
    await stop_background_tasks()
    print("Smart FCU Simulator stopped")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Non-intrusive Plug-and-Play Adaptive HVAC Control System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(zones_router)
app.include_router(devices_router)
app.include_router(sensors_router)
app.include_router(predictions_router)
app.include_router(websocket_router)
app.include_router(chat_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.app_name}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
