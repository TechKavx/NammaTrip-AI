from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.db import Base


class Place(Base):
    __tablename__ = "places"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str] = mapped_column(String(100), index=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), default="India")
    category: Mapped[str | None] = mapped_column(String(300), nullable=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    address: Mapped[str | None] = mapped_column(String(300), nullable=True)
    opening_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    closing_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ticket_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    average_visit_duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    popularity: Mapped[float | None] = mapped_column(Float, nullable=True)
    indoor_outdoor: Mapped[str | None] = mapped_column(String(30), nullable=True)
    family_friendly: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    photography_friendly: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    nature_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    adventure_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    culture_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    food_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
