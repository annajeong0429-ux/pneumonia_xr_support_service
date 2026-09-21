from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.dependencies import get_current_user, require_admin
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.models.user import Department, Role, User
from app.repositories import user_repository
from app.schemas.user import (
    LoginRequest,
    MessageResponse,
    MyPageResponse,
    PasswordChangeRequest,
    RoleUpdateRequest,
    SignupRequest,
    TokenResponse,
    UserListItem,
    UserResponse,
    UserUpdateRequest,
    WithdrawRequest,
)

user_router = APIRouter(prefix="/api/v1/users", tags=["users"])
auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


# REQ-USER-001 회원가입
@user_router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: SignupRequest, db: AsyncSession = Depends(async_get_db)):
    if await user_repository.get_by_email(db, body.email) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 존재하는 이메일입니다.")

    if await user_repository.get_by_phone(db, body.phone_number) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 존재하는 휴대폰 번호입니다.")

    hashed = hash_password(body.password)

    user = await user_repository.create(db, email=body.email, hashed_password=hashed, name=body.name, department=body.department, gender=body.gender, phone_number=body.phone_number, role=Role.PENDING)
    return user



# REQ-USER-002 
@auth_router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, response: Response, db: AsyncSession = Depends(async_get_db)):
    user = await user_repository.get_by_email(db, body.email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='이메일 또는 비밀번호가 일치하지 않습니다.')

    if verify_password(body.password, user.hashed_password) is False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="이메일 또는 비밀번호가 일치하지 않습니다.")

    access_token= create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, max_age=60*60*24*7)

    return TokenResponse(access_token=access_token)


# REQ-USER-003 로그아웃
@auth_router.post("/logout", response_model=MessageResponse)
async def logout(response: Response, current_user: User = Depends(get_current_user)):
    response.delete_cookie('refresh_token')
    return MessageResponse(message='로그아웃 되었습니다.')



# REQ-USER-004 회원 목록 조회 (Admin 전용)
@user_router.get("", response_model=list[UserListItem])
async def list_all_users(
    search: str | None = None,
    department: Department | None = None,
    db: AsyncSession = Depends(async_get_db),
    _: User = Depends(require_admin),
):
    return await user_repository.list_users(db, search=search, department=department)


# REQ-USER-006 마이페이지 조회
@user_router.get("/me", response_model=MyPageResponse)
async def get_my_page(current_user: User = Depends(get_current_user)):
    return current_user
    # TODO: current_user 그대로 return (MyPageResponse가 자동 변환)
    raise NotImplementedError


# REQ-USER-007 회원 정보 수정
@user_router.patch("/me", response_model=MessageResponse)
async def update_my_info(
    body: UserUpdateRequest,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user),
):
    if body.phone_number is not None:
        existing = await user_repository.get_by_phone(db, body.phone_number)
        if existing is not None and existing.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='이미사용중인 휴대폰 번호입니다.')

    update_fields = body.model_dump(exclude_none = True)
    await user_repository.update(db, current_user, **update_fields)
    return MessageResponse(message='수정되었습니다.')    


# REQ-USER-008 비밀번호 변경
@user_router.put("/me/password", response_model=MessageResponse)
async def change_password(
    body: PasswordChangeRequest,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user),
):
    if verify_password(body.old_password, current_user.hashed_password) is False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='비밀번호가 일치하지 않습니다.')

    update_password = hash_password(body.new_password)
    await user_repository.update(db, current_user,hashed_password=update_password)
    return MessageResponse(message='비밀번호가 변경되었습니다')



# REQ-USER-009 회원 탈퇴
@user_router.delete("/me", response_model=MessageResponse)
async def withdraw(
    body: WithdrawRequest,
    db: AsyncSession = Depends(async_get_db),
    current_user: User = Depends(get_current_user),
):
    if verify_password(body.password, current_user.hashed_password) is False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='비밀번호가 일치하지 않습니다.')

    await user_repository.delete(db, current_user)
    return MessageResponse(message='회원탈퇴 되었습니다.')

# REQ-USER-005 회원 권한 변경 (Admin 전용)
# 주의: 이 라우트는 반드시 /me 관련 라우트들보다 "아래"에 있어야 함!
# ({user_id}가 문자열 "me"까지 가로챌 수 있어서 순서가 중요함 - main.py의 catch_all 때와 같은 이유)
@user_router.patch("/{user_id}", response_model=UserResponse)
async def change_user_role(
    user_id: int,
    body: RoleUpdateRequest,
    db: AsyncSession = Depends(async_get_db),
    _: User = Depends(require_admin),
):
    user  = await user_repository.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='id가 존재하지 않습니다.')

    user = await user_repository.update(db, user, role=body.role)
    return user
    

