from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.medical_record import MedicalRecords


async def get_by_id(db: AsyncSession, record_id: int) -> MedicalRecords | None:
    result = await db.execute(select(MedicalRecords).where(MedicalRecords.id == record_id))
    return result.scalar_one_or_none()


async def get_by_chart_number(db: AsyncSession, chart_number: str) -> MedicalRecords | None:
    result = await db.execute(select(MedicalRecords).where(MedicalRecords.chart_number == chart_number))
    return result.scalar_one_or_none()


async def list_by_patient(db: AsyncSession, patient_id: int) -> list[MedicalRecords]:
    result = await db.execute(select(MedicalRecords).where(MedicalRecords.patient_id == patient_id))
    return list(result.scalars().all())


async def create(db: AsyncSession, **fields) -> MedicalRecords:
    record = MedicalRecords(**fields)
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record
