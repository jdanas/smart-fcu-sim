from sqlalchemy import String, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional
from app.database import Base


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'fcu', 'sensor'
    zone_id: Mapped[Optional[str]] = mapped_column(
        String(50), ForeignKey("zones.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="offline"
    )  # 'online', 'offline', 'syncing'
    discovered_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
