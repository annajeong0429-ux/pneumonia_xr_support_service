from datetime import datetime

from pydantic import BaseModel


class MedicalRecordListItem(BaseModel):
    id: int
    chart_number: str
    symptoms: str
    created_at: datetime


class MedicalRecordCreateResponse(BaseModel):
    id: int
    chart_number: str
    symptoms: str
    created_at: datetime
    xray_image_url: str


class MedicalRecordDetailResponse(BaseModel):
    id: int
    patient_id: int
    chart_number: str
    symptoms: str
    xray_image_url: str | None
    created_at: datetime
