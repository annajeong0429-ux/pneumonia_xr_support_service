import enum

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import SmallInteger

from app.core.db.databases import Base
from app.core.db.models import TimestampMixin

class Gender(str, enum.Enum):
    M = 'M'
    F = 'F'

class Patient(Base, TimestampMixin):
    __tablename__ = "patients"
    id: Mapped[int] = mapped_column(primary_key= True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30))
    age : Mapped[int] = mapped_column(SmallInteger)
    gender : Mapped[Gender | None] = mapped_column(Enum(Gender), nullable=True)
    phone : Mapped[str] = mapped_column(String(11))
