import enum

from sqlalchemy import Enum, String, ForeignKey, Text, Boolean, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal

from app.core.db.databases import Base
from app.core.db.models import TimestampMixin

class Ai_analysis_results(Base, TimestampMixin):
    __tablename__ = 'ai_analysis_results'
    id :Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    record_id : Mapped[int] = mapped_column(ForeignKey('medical_records.id', ondelete='CASCADE'))
    is_pneumonia : Mapped[bool] = mapped_column(Boolean)
    confidence : Mapped[Decimal] = mapped_column(DECIMAL(precision=5, scale=2))
    heatmap_url : Mapped[str] = mapped_column(String(255))
    ai_model : Mapped[str] = mapped_column(String(50))
    