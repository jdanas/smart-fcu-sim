from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import Zone
from app.schemas import ZoneResponse, ZoneUpdate, SetpointUpdate, AdaptiveModeUpdate

router = APIRouter(prefix="/api/zones", tags=["zones"])


@router.get("", response_model=List[ZoneResponse])
async def get_zones(db: AsyncSession = Depends(get_db)):
    """Get all zones."""
    result = await db.execute(select(Zone))
    zones = result.scalars().all()
    return zones


@router.get("/{zone_id}", response_model=ZoneResponse)
async def get_zone(zone_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific zone by ID."""
    result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = result.scalar_one_or_none()

    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    return zone


@router.put("/{zone_id}/setpoint", response_model=ZoneResponse)
async def update_setpoint(
    zone_id: str, data: SetpointUpdate, db: AsyncSession = Depends(get_db)
):
    """Update zone temperature setpoint."""
    result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = result.scalar_one_or_none()

    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    zone.setpoint = data.setpoint
    await db.commit()
    await db.refresh(zone)

    return zone


@router.put("/{zone_id}/adaptive", response_model=ZoneResponse)
async def update_adaptive_mode(
    zone_id: str, data: AdaptiveModeUpdate, db: AsyncSession = Depends(get_db)
):
    """Toggle adaptive control mode."""
    result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = result.scalar_one_or_none()

    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    zone.adaptive_mode = data.adaptive_mode
    await db.commit()
    await db.refresh(zone)

    return zone


@router.patch("/{zone_id}", response_model=ZoneResponse)
async def update_zone(
    zone_id: str, data: ZoneUpdate, db: AsyncSession = Depends(get_db)
):
    """Update zone properties."""
    result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = result.scalar_one_or_none()

    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(zone, field, value)

    await db.commit()
    await db.refresh(zone)

    return zone
