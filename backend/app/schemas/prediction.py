from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class PredictionBase(BaseModel):
    current_temp: float
    predicted_temp: float
    confidence: float = 0.85
    prediction_horizon_minutes: int = 15
    trend: str = "stable"  # 'rising', 'falling', 'stable'


class PredictionResponse(PredictionBase):
    id: int
    zone_id: str
    timestamp: datetime

    class Config:
        from_attributes = True


class ZonePrediction(BaseModel):
    zone_id: str
    current_temp: float
    predicted_temp: float
    confidence: float
    prediction_horizon_minutes: int
    trend: str
    timestamp: datetime


class PredictionDataPoint(BaseModel):
    timestamp: datetime
    current_temp: float
    predicted_temp: float


class PredictionHistory(BaseModel):
    zone_id: str
    data: List[PredictionDataPoint]


class RealtimePredictionEvent(BaseModel):
    type: str = "prediction"
    zone_id: str
    current_temp: float
    predicted_temp: float
    confidence: float
    trend: str
    timestamp: datetime
