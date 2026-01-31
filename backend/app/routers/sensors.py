from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models import SensorReading, Zone
from app.schemas import SensorReadingResponse, ZoneSensorHistory, SensorDataPoint

router = APIRouter(prefix="/api/sensors", tags=["sensors"])


@router.get("/readings", response_model=List[SensorReadingResponse])
async def get_readings(
    zone_id: Optional[str] = Query(default=None),
    device_id: Optional[str] = Query(default=None),
    limit: int = Query(default=100, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """Get sensor readings, optionally filtered by zone or device."""
    query = select(SensorReading).order_by(desc(SensorReading.timestamp)).limit(limit)

    if zone_id:
        query = query.where(SensorReading.zone_id == zone_id)
    if device_id:
        query = query.where(SensorReading.device_id == device_id)

    result = await db.execute(query)
    readings = result.scalars().all()
    return readings


@router.get("/zones/{zone_id}/history", response_model=ZoneSensorHistory)
async def get_zone_sensor_history(
    zone_id: str,
    minutes: int = Query(default=60, le=1440),
    db: AsyncSession = Depends(get_db),
):
    """Get sensor reading history for a zone."""
    # Verify zone exists
    zone_result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = zone_result.scalar_one_or_none()

    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    # Get readings within time window
    cutoff = datetime.now() - timedelta(minutes=minutes)

    query = (
        select(SensorReading)
        .where(SensorReading.zone_id == zone_id)
        .where(SensorReading.timestamp >= cutoff)
        .order_by(SensorReading.timestamp)
    )

    result = await db.execute(query)
    readings = result.scalars().all()

    # Convert to data points
    data_points = [
        SensorDataPoint(
            timestamp=r.timestamp,
            temperature=r.temperature,
            humidity=r.humidity,
            co2_level=r.co2_level,
            power_kw=r.power_kw,
            occupancy=r.occupancy,
        )
        for r in readings
    ]

    return ZoneSensorHistory(zone_id=zone_id, readings=data_points)


@router.get("/zones/{zone_id}/latest", response_model=SensorDataPoint)
async def get_zone_latest_reading(zone_id: str, db: AsyncSession = Depends(get_db)):
    """Get the latest sensor reading for a zone."""
    query = (
        select(SensorReading)
        .where(SensorReading.zone_id == zone_id)
        .order_by(desc(SensorReading.timestamp))
        .limit(1)
    )

    result = await db.execute(query)
    reading = result.scalar_one_or_none()

    if not reading:
        raise HTTPException(status_code=404, detail="No readings found for zone")

    return SensorDataPoint(
        timestamp=reading.timestamp,
        temperature=reading.temperature,
        humidity=reading.humidity,
        co2_level=reading.co2_level,
        power_kw=reading.power_kw,
        occupancy=reading.occupancy,
    )
