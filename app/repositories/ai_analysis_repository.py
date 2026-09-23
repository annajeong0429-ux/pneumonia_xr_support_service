from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_analysis_result import Ai_analysis_results


async def get_by_record_and_model(
    db: AsyncSession, record_id: int, ai_model: str
) -> Ai_analysis_results | None:
    result = await db.execute(
        select(Ai_analysis_results).where(
            Ai_analysis_results.record_id == record_id,
            Ai_analysis_results.ai_model == ai_model,
        )
    )
    return result.scalar_one_or_none()


async def list_by_record(db: AsyncSession, record_id: int) -> list[Ai_analysis_results]:
    result = await db.execute(
        select(Ai_analysis_results).where(Ai_analysis_results.record_id == record_id)
    )
    return list(result.scalars().all())


async def create(db: AsyncSession, **fields) -> Ai_analysis_results:
    analysis = Ai_analysis_results(**fields)
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    return analysis
