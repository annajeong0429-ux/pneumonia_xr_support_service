import enum

from sqlalchemy import Enum, String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.databases import Base
from app.core.db.models import TimestampMixin

class MedicalRecords(Base, TimestampMixin):
    __tablename__ = 'medical_records'
    id :Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    patient_id : Mapped[int] = mapped_column(ForeignKey('patients.id',ondelete='CASCADE'))
    chart_number : Mapped[str] = mapped_column(String(50), unique=True)
    symptoms : Mapped[str] = mapped_column(Text)
