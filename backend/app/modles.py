from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base

class UAV(Base):
    __tablename__ = "uavs"

    id = Column(String, primary_key=True, index=True)
    type = Column(String, nullable=False)  # commercial, emergency, recreational
    status = Column(String, default="idle")  # idle, flying, emergency, maintenance
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    altitude = Column(Float, nullable=True)
    battery_level = Column(Float, default=100.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
