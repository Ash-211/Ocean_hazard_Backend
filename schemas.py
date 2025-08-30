# schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class HazardReportBase(BaseModel):
    hazard_type: str
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    severity: int
    description: Optional[str] = None

class HazardReportCreate(HazardReportBase):
    pass

class HazardReport(BaseModel):
    id: uuid.UUID
    hazard_type: str
    severity: int
    description: Optional[str] = None
    report_time: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        # Extract latitude and longitude from geometry if available
        data = {
            "id": obj.id,
            "hazard_type": obj.hazard_type,
            "severity": obj.severity,
            "description": obj.description,
            "report_time": obj.report_time
        }
        return cls(**data)
