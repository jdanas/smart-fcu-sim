from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class SensorReadingBase(BaseModel):
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    co2_level: Optional[float] = None
    power_kw: Optional[float] = None
    occupancy: Optional[int] = None


class SensorReadingCreate(SensorReadingBase):
    device_id: str
    zone_id: str


class SensorReadingResponse(SensorReadingBase):
    id: int
    device_id: str
    zone_id: str
    timestamp: datetime

    class Config:
        from_attributes = True


class SensorDataPoint(BaseModel):
    timestamp: datetime
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    co2_level: Optional[float] = None
    power_kw: Optional[float] = None
    occupancy: Optional[int] = None


class ZoneSensorHistory(BaseModel):
    zone_id: str
    readings: List[SensorDataPoint]


class RealtimeSensorEvent(BaseModel):
    type: str = "reading"
    zone_id: str
    device_id: str
    data: SensorReadingBase
    timestamp: datetime
