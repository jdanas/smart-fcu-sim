from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ZoneBase(BaseModel):
    name: str
    setpoint: float = 22.0
    adaptive_mode: bool = True


class ZoneCreate(ZoneBase):
    id: str


class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    setpoint: Optional[float] = None
    adaptive_mode: Optional[bool] = None


class ZoneResponse(ZoneBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SetpointUpdate(BaseModel):
    setpoint: float


class AdaptiveModeUpdate(BaseModel):
    adaptive_mode: bool
