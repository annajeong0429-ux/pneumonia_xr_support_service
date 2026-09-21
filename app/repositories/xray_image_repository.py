from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.xray_image import XrayImage


async def get_by_record_id(db: AsyncSession, record_id: int) -> XrayImage | None:
    result = await db.execute(select(XrayImage).where(XrayImage.record_id == record_id))
    return result.scalar_one_or_none()


async def create(db: AsyncSession, **fields) -> XrayImage:
    xray = XrayImage(**fields)
    db.add(xray)
    await db.commit()
    await db.refresh(xray)
    return xray
