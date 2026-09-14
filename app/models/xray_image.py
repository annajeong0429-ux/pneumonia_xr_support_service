import enum

from sqlalchemy import Enum, String , ForeignKey, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime , UTC

from app.core.db.databases import Base

class XrayImage(Base):
    __tablename__ ='xray_images'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    record_id : Mapped[int] = mapped_column(ForeignKey('medical_records.id',ondelete='CASCADE'))
    uploader_id : Mapped[int | None] = mapped_column(ForeignKey('users.id',ondelete='SET NULL'))
    image_url : Mapped[str] = mapped_column(String(2048))
    shooting_datetime : Mapped[datetime] = mapped_column(DateTime)
    created_at :Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC),server_default=text("current_timestamp(0)"))