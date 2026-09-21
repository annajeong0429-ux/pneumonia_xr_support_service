from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.dependencies import require_medical_staff, require_staff_or_admin
from app.models.user import Gender, User
from app.repositories import medical_record_repository, patient_repository
from app.schemas.medical_record import MedicalRecordListItem
from app.schemas.patient import PatientCreate, PatientDetailResponse, PatientListItem, PatientUpdate
from app.schemas.user import MessageResponse

patient_router = APIRouter(prefix="/api/v1/patients", tags=["patients"])


# REQ-PTNT-001 환자 정보 등록
@patient_router.post("", response_model=PatientListItem, status_code=status.HTTP_201_CREATED)
async def create_patient(
    body: PatientCreate,
    db: AsyncSession = Depends(async_get_db),
    _: User = Depends(require_medical_staff),
):
    return await patient_repository.create(db, name=body.name, age=body.age, gender=body.gender, phone=body.phone)



# REQ-PTNT-002 환자 목록 조회
@patient_router.get("", response_model=list[PatientListItem])
async def list_patients(
    name: str | None = None,
    gender: Gender | None = None,
    min_age: int | None = None,
    max_age: int | None = None,
    db: AsyncSession = Depends(async_get_db),
    _: User = Depends(require_staff_or_admin),
):
    return await patient_repository.list_patients(db, name=name, gender=gender, min_age=min_age, max_age=max_age)


# REQ-PTNT-003 환자 정보 상세 조회
@patient_router.get("/{patient_id}", response_model=PatientDetailResponse)
async def get_patient_detail(
    patient_id: int,
    db: AsyncSession = Depends(async_get_db),
    _: User = Depends(require_staff_or_admin),
):
    patient = await patient_repository.get_by_id(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail='환자 목록에 없는 id입니다')
    
    return patient



# REQ-PTNT-004 환자 정보 수정
@patient_router.patch("/{patient_id}", response_model=MessageResponse)
async def update_patient(
    patient_id: int,
    body: PatientUpdate,
    db: AsyncSession = Depends(async_get_db),
    _: User = Depends(require_staff_or_admin),
):
    patient = await patient_repository.get_by_id(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail='환자 목록에 없는 id입니다')
    update_fields = body.model_dump(exclude_none=True)
    await patient_repository.update(db, patient, **update_fields)
    return MessageResponse(message='수정되었습니다')


# REQ-PTNT-005 환자 정보 삭제
@patient_router.delete("/{patient_id}", response_model=MessageResponse)
async def delete_patient(
    patient_id: int,
    db: AsyncSession = Depends(async_get_db),
    _: User = Depends(require_staff_or_admin),
):
    patient = await patient_repository.get_by_id(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail='환자목록에 없는 id입니다.')
    await patient_repository.delete(db, patient)
    return MessageResponse(message='환자 정보가 삭제되었습니다')


# REQ-MDR-002 특정 환자의 진료기록 목록 조회
@patient_router.get("/{patient_id}/medical-records", response_model=list[MedicalRecordListItem])
async def list_patient_medical_records(
    patient_id: int,
    db: AsyncSession = Depends(async_get_db),
    _: User = Depends(require_staff_or_admin),
):
    patient = await patient_repository.get_by_id(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail='환자목록에 없는 id입니다.')
    records = await medical_record_repository.list_by_patient(db, patient_id)
    result = []
    for record in records:
        summary = record.symptoms if len(record.symptoms) <= 100 else record.symptoms[:100]+"..."
        result.append(MedicalRecordListItem(id=record.id, chart_number=record.chart_number, symptoms=summary, created_at=record.created_at,))
    return result
