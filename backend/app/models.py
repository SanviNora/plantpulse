from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32))


class DemandFact(Base):
    __tablename__ = "fact_demand"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    week: Mapped[int] = mapped_column(Integer, index=True)
    sku_code: Mapped[str] = mapped_column(String(16), index=True)
    dc_code: Mapped[str] = mapped_column(String(8), index=True)
    forecast_units: Mapped[float] = mapped_column(Float)
    actual_units: Mapped[float] = mapped_column(Float)
    on_hand: Mapped[float] = mapped_column(Float)
    incoming: Mapped[float] = mapped_column(Float)


class CapacityFact(Base):
    __tablename__ = "fact_capacity"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    week: Mapped[int] = mapped_column(Integer, index=True)
    plant_code: Mapped[str] = mapped_column(String(8), index=True)
    hours_available: Mapped[float] = mapped_column(Float)
    hours_used: Mapped[float] = mapped_column(Float)


class ScrapFact(Base):
    __tablename__ = "fact_scrap"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    week: Mapped[int] = mapped_column(Integer, index=True)
    plant_code: Mapped[str] = mapped_column(String(8), index=True)
    sku_code: Mapped[str] = mapped_column(String(16), index=True)
    units: Mapped[float] = mapped_column(Float)
    scrap_units: Mapped[float] = mapped_column(Float)


class ExceptionAck(Base):
    __tablename__ = "exception_acks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
