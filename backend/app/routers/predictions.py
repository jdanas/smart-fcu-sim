from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime, timedelta
from typing import List

from app.database import get_db
from app.models import SensorReading, Zone, Prediction
from app.schemas import ZonePrediction, PredictionHistory, PredictionDataPoint
from app.services import prediction_engine

router = APIRouter(prefix="/api/predictions", tags=["predictions"])


@router.get("/{zone_id}", response_model=ZonePrediction)
async def get_zone_prediction(zone_id: str, db: AsyncSession = Depends(get_db)):
    """Get current AI prediction for a zone."""
    # Verify zone exists
    zone_result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = zone_result.scalar_one_or_none()

    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    # Get recent readings for prediction (last 5 minutes)
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

    # Extract temperatures
    temps = [r.temperature for r in readings if r.temperature is not None]

    if not temps:
        # No recent data - return defaults
        return ZonePrediction(
            zone_id=zone_id,
            current_temp=zone.setpoint,
            predicted_temp=zone.setpoint,
            confidence=0.5,
            prediction_horizon_minutes=15,
            trend="stable",
            timestamp=datetime.now(),
        )

    current_temp = temps[-1]
    predicted_temp, confidence, trend = prediction_engine.predict(temps)

    return ZonePrediction(
        zone_id=zone_id,
        current_temp=current_temp,
        predicted_temp=predicted_temp,
        confidence=confidence,
        prediction_horizon_minutes=15,
        trend=trend,
        timestamp=datetime.now(),
    )


@router.get("/{zone_id}/history", response_model=PredictionHistory)
async def get_prediction_history(
    zone_id: str, minutes: int = 60, db: AsyncSession = Depends(get_db)
):
    """Get prediction history for a zone."""
    # Verify zone exists
    zone_result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = zone_result.scalar_one_or_none()

    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    # Get stored predictions
    cutoff = datetime.now() - timedelta(minutes=minutes)
    query = (
        select(Prediction)
        .where(Prediction.zone_id == zone_id)
        .where(Prediction.timestamp >= cutoff)
        .order_by(Prediction.timestamp)
    )

    result = await db.execute(query)
    predictions = result.scalars().all()

    data_points = [
        PredictionDataPoint(
            timestamp=p.timestamp,
            current_temp=p.current_temp,
            predicted_temp=p.predicted_temp,
        )
        for p in predictions
    ]

    return PredictionHistory(zone_id=zone_id, data=data_points)
