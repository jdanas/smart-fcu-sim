from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import Device
from app.schemas import DeviceResponse, DeviceStatusUpdate

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.get("", response_model=List[DeviceResponse])
async def get_devices(
    zone_id: Optional[str] = Query(default=None),
    device_type: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Get all devices, optionally filtered by zone or type."""
    query = select(Device)

    if zone_id:
        query = query.where(Device.zone_id == zone_id)
    if device_type:
        query = query.where(Device.type == device_type)

    result = await db.execute(query)
    devices = result.scalars().all()
    return devices


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific device by ID."""
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return device


@router.put("/{device_id}/status", response_model=DeviceResponse)
async def update_device_status(
    device_id: str, data: DeviceStatusUpdate, db: AsyncSession = Depends(get_db)
):
    """Update device status."""
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    device.status = data.status
    device.last_seen = datetime.now()
    await db.commit()
    await db.refresh(device)

    return device


@router.delete("/{device_id}")
async def delete_device(device_id: str, db: AsyncSession = Depends(get_db)):
    """Remove a device."""
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    await db.delete(device)
    await db.commit()

    return {"message": f"Device {device_id} deleted"}
