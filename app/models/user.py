import enum

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.databases import Base
from app.core.db.models import TimestampMixin

class Gender(str, enum.Enum):
    M = 'M'
    F = 'F'

class Department(str, enum.Enum):
    MEDICAL ='MEDICAL'
    DEV = 'DEV'
    RESEARCH ='RESEARCH'

class Role(str, enum.Enum):
    PENDING = 'PENDING'
    STAFF = 'STAFF'
    ADMIN = 'ADMIN'

class User(Base, TimestampMixin):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email : Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password : Mapped[str] = mapped_column(String(255))
    name : Mapped[str] = mapped_column(String(20))
    phone_number : Mapped[str] = mapped_column(String(20),unique=True)
    gender : Mapped[Gender] = mapped_column(Enum(Gender))
    department : Mapped[Department] = mapped_column(Enum(Department))
    role : Mapped[Role] = mapped_column(Enum(Role))
    is_active : Mapped[bool] = mapped_column(Boolean, default=True)
