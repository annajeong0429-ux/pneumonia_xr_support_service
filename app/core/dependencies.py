from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import jwt

from app.core.db.databases import async_get_db
from app.core.security import decode_token
from app.models.user import Department, Role, User

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(async_get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get("user_id")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return current_user


async def require_staff_or_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role == Role.PENDING:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="접근 권한이 없습니다.")
    return current_user


async def require_medical_staff(current_user: User = Depends(require_staff_or_admin)) -> User:
    if current_user.department != Department.MEDICAL:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="의료 부서만 접근 가능합니다.")
    return current_user
