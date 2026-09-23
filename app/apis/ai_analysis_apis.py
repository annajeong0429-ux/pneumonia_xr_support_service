from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.concurrency import run_in_threadpool
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.dependencies import require_staff_or_admin
from app.models.user import User
from app.repositories import ai_analysis_repository, medical_record_repository, xray_image_repository
from app.schemas.ai_analysis import AiAnalysisResponse
from worker.model import predict_pneumonia

BASE_DIR = Path(__file__).resolve().parent.parent.parent
AI_MODEL_NAME = "convnext_densenet_OR"

ai_analysis_router = APIRouter(prefix="/api/v1/records", tags=["ai-analysis"])


# REQ-PRED-001 AI 모델 활용 폐렴 예측
@ai_analysis_router.post("/{record_id}/ai-analysis", response_model=AiAnalysisResponse)
async def run_ai_analysis(
    record_id: int,
    response: Response,
    db: AsyncSession = Depends(async_get_db),
    _: User = Depends(require_staff_or_admin),
):
    record = await medical_record_repository.get_by_id(db, record_id)
    if record is None:
        raise HTTPException(status_code=404 , detail='차트에 저장된 아이디가 없습니다')

    existing = await ai_analysis_repository.get_by_record_and_model(db, record_id, AI_MODEL_NAME)
    if existing is not None:
        response.status_code = status.HTTP_200_OK
        return existing

    xray = await xray_image_repository.get_by_record_id(db, record_id)
    if xray is None:
        raise HTTPException(status_code=400, detail='진료기록에 x-ray 이미지가 없습니다.')

    image_path = BASE_DIR / xray.image_url.lstrip("/")
    image = Image.open(image_path)

    result = await run_in_threadpool(predict_pneumonia, image)

    new_analysis = await ai_analysis_repository.create(db, record_id=record_id, is_pneumonia=result['is_pneumonia'],
                                                        confidence=result['confidence'], heatmap_url=None, ai_model=AI_MODEL_NAME,)

    response.status_code = status.HTTP_201_CREATED 
    return new_analysis 



# REQ-PRED-002 AI 모델 활용 폐렴 예측 결과 조회
@ai_analysis_router.get("/{record_id}/ai-analysis", response_model=list[AiAnalysisResponse])
async def list_ai_analysis(
    record_id: int,
    db: AsyncSession = Depends(async_get_db),
    _: User = Depends(require_staff_or_admin),
):
    record = await medical_record_repository.get_by_id(db, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail='진료기록에 등록된 내용이 없습니다')
    return await ai_analysis_repository.list_by_record(db, record_id)
