import re

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.models.user import Department, Gender, Role

EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
PASSWORD_PATTERN = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,20}$"


def _validate_email_format(v: str) -> str:
    if not re.match(EMAIL_PATTERN, v):
        raise ValueError("올바른 이메일 형식이 아닙니다")
    return v


def _validate_password_complexity(v: str) -> str:
    if not re.match(PASSWORD_PATTERN, v):
        raise ValueError("비밀번호는 대문자, 소문자, 특수문자를 포함한 8~20자여야 합니다")
    return v


class SignupRequest(BaseModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=20)
    name: str = Field(min_length=2, max_length=20)
    department: Department
    gender: Gender
    phone_number: str = Field(max_length=20)

    _check_email = field_validator("email")(_validate_email_format)
    _check_password = field_validator("password")(_validate_password_complexity)


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    department: Department
    gender: Gender
    phone_number: str
    is_active: bool
    role: Role

    model_config = {"from_attributes": True}


class UserListItem(BaseModel):
    id: int
    email: str
    name: str
    department: Department
    gender: Gender
    phone_number: str
    is_active: bool

    model_config = {"from_attributes": True}


class MyPageResponse(BaseModel):
    name: str
    email: str
    department: Department
    gender: Gender
    phone_number: str
    role: Role

    model_config = {"from_attributes": True}


class RoleUpdateRequest(BaseModel):
    role: Role


class UserUpdateRequest(BaseModel):
    department: Department | None = None
    phone_number: str | None = Field(default=None, max_length=20)

    @model_validator(mode="after")
    def check_at_least_one(self):
        if self.department is None and self.phone_number is None:
            raise ValueError("수정할 항목이 없습니다")
        return self


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, max_length=20)

    _check_new_password = field_validator("new_password")(_validate_password_complexity)


class WithdrawRequest(BaseModel):
    password: str
