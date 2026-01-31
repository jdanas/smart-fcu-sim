from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    zone_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("zones.id"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    current_temp: Mapped[float] = mapped_column(Float, nullable=False)
    predicted_temp: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.85)
    prediction_horizon_minutes: Mapped[int] = mapped_column(Integer, default=15)
    trend: Mapped[str] = mapped_column(
        String(20), default="stable"
    )  # 'rising', 'falling', 'stable'
