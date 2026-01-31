from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional
from app.database import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("devices.id"), nullable=False
    )
    zone_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("zones.id"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    humidity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    co2_level: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    power_kw: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    occupancy: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
