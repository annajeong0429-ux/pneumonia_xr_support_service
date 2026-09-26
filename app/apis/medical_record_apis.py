from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.dependencies import require_medical_staff, require_staff_or_admin
from app.core.storage import save_xray_image
from app.models.user import User
from app.repositories import medical_record_repository, patient_repository, xray_image_repository
from app.schemas.medical_record import MedicalRecordCreateResponse, MedicalRecordDetailResponse

from datetime import UTC, datetime

medical_record_router = APIRouter(prefix="/api/v1/medical-records", tags=["medical-records"])


# REQ-MDR-001 진료기록 등록
# 주의: X-ray 이미지 "파일"을 같이 받아야 해서, 다른 API들과 다르게
#      순수 JSON body가 아니라 Form(텍스트 필드) + File(파일)을 씀 (multipart/form-data)
@medical_record_router.post(
    "", response_model=MedicalRecordCreateResponse, status_code=status.HTTP_201_CREATED
)
async def create_medical_record(
    patient_id: int = Form(...),
    chart_number: str = Form(...),
    symptoms: str = Form(...),
    xray_image: UploadFile = File(...),
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(require_medical_staff),
):
    patient = await patient_repository.get_by_id(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail='조회목록에 해당 id가 없습니다.')
    
    if await medical_record_repository.get_by_chart_number(db, chart_number) is not None:
        raise HTTPException(status_code=409, detail='해당 차트번호가 이미 존재합니다.')

    record = await medical_record_repository.create(db, patient_id=patient_id, chart_number=chart_number,symptoms=symptoms)

    image_url = await save_xray_image(xray_image)
    await xray_image_repository.create(db, record_id=record.id, uploader_id=current_user.id, image_url=image_url, shooting_datetime=datetime.now(UTC),)

    return MedicalRecordCreateResponse(id=record.id, chart_number=record.chart_number, symptoms=record.symptoms,created_at=record.created_at, xray_image_url=image_url,)


# REQ-MDR-003 진료기록 상세 조회
@medical_record_router.get("/{record_id}", response_model=MedicalRecordDetailResponse)
async def get_medical_record_detail(
    record_id: int,
    db: AsyncSession = Depends(async_get_db),
    _: User = Depends(require_staff_or_admin),
):
    record = await medical_record_repository.get_by_id(db, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail='차트에 없는 아이디 입니다')

    xray = await xray_image_repository.get_by_record_id(db, record_id)

    return MedicalRecordDetailResponse(
        id=record_id, patient_id=record.patient_id, chart_number=record.chart_number,
        symptoms=record.symptoms, xray_image_url=xray.image_url if xray is not None else None,
        created_at=record.created_at,)
    