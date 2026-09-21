from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.models.user import Gender


class PatientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=30)
    age: int = Field(ge=0)
    gender: Gender
    phone: str = Field(max_length=11)


class PatientUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=30)
    phone: str | None = Field(default=None, max_length=11)

    @model_validator(mode="after")
    def check_at_least_one(self):
        if self.name is None and self.phone is None:
            raise ValueError("수정할 항목이 없습니다")
        return self


class PatientListItem(BaseModel):
    id: int
    name: str
    age: int
    gender: Gender | None
    phone: str
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class PatientDetailResponse(BaseModel):
    name: str
    gender: Gender | None
    phone: str
    age: int

    model_config = {"from_attributes": True}
