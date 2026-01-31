from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DeviceBase(BaseModel):
    name: str
    type: str  # 'fcu', 'sensor'
    zone_id: Optional[str] = None
    status: str = "offline"


class DeviceCreate(DeviceBase):
    id: str


class DeviceResponse(DeviceBase):
    id: str
    discovered_at: datetime
    last_seen: Optional[datetime] = None
    metadata_json: Optional[dict] = None

    class Config:
        from_attributes = True


class DeviceStatusUpdate(BaseModel):
    status: str


class DeviceDiscoveryEvent(BaseModel):
    type: str = "device_discovered"
    device: DeviceResponse
