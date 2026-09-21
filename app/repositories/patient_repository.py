from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient
from app.models.user import Gender


async def get_by_id(db: AsyncSession, patient_id: int) -> Patient | None:
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    return result.scalar_one_or_none()


async def list_patients(
    db: AsyncSession,
    name: str | None = None,
    gender: Gender | None = None,
    min_age: int | None = None,
    max_age: int | None = None,
) -> list[Patient]:
    query = select(Patient)
    if name:
        query = query.where(Patient.name.contains(name))
    if gender:
        query = query.where(Patient.gender == gender)
    if min_age is not None:
        query = query.where(Patient.age >= min_age)
    if max_age is not None:
        query = query.where(Patient.age <= max_age)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create(db: AsyncSession, **fields) -> Patient:
    patient = Patient(**fields)
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


async def update(db: AsyncSession, patient: Patient, **fields) -> Patient:
    for key, value in fields.items():
        setattr(patient, key, value)
    await db.commit()
    await db.refresh(patient)
    return patient


async def delete(db: AsyncSession, patient: Patient) -> None:
    await db.delete(patient)
    await db.commit()
