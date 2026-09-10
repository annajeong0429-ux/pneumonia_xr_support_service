import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator

router = APIRouter(prefix="/practice_api", tags=["practice"])

user_list = [
    {"id":1, "name": "정다이", "age": 24, "email":"dayi@example.com", "password":"Test12345@"},
    {"id":2, "name": "김도은", "age": 30, "email":"doeun@example.com", "password":"Test12345#"},
    {"id":3, "name": "박지민", "age": 28, "email":"jimin@example.com", "password":"Test12345$"}
]

@router.get("/users")
async def get_users():
    result = []
    for user in user_list:
        result.append({"id":user["id"], "name":user["name"], "age":user["age"], "email":user["email"]})
    return result

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    for user in user_list:
        if user["id"] == user_id:
            return {"id":user["id"], "name":user["name"], "age":user["age"], "email":user["email"]}
    raise HTTPException(status_code=404, detail="User not found")

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=10)
    age : int = Field(ge=14)
    email : str = Field(max_length=30)
    password : str = Field(min_length=8, max_length=20)

    @field_validator("email")
    @classmethod
    def check_email_format(cls, v):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("password")
    @classmethod
    def check_password_complexity(cls, v):
        pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,}$"
        if not re.match(pattern, v):
            raise ValueError("Password must include uppercase, lowercase, number, and special character")
        return v

class UserUpdate(BaseModel):
    age : int | None = Field(default=None, ge=14)
    email : str | None = Field(default=None, max_length=30)
    password : str | None = Field(default=None, min_length=8, max_length=20)
    @field_validator("email")
    @classmethod
    def check_email_format(cls, v):
        if v is None:
            return v
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("password")
    @classmethod
    def check_password_complexity(cls, v):
        if v is None:
            return v
        pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,}$"
        if not re.match(pattern, v):
            raise ValueError("Password must include uppercase, lowercase, number, and special character")
        return v

@router.post("/users")
async def create_user(user: UserCreate):
    # Check if the email already exists
    for existing_user in user_list:
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create a new user ID
    new_id = max(user["id"] for user in user_list) + 1
    new_user = {"id": new_id, **user.model_dump()}
    user_list.append(new_user)
    return new_user


@router.put("/users/{user_id}")
async def update_user(user_id: int, updated_user: UserUpdate):
    if updated_user.age is None and updated_user.email is None and updated_user.password is None:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    for user in user_list:
        if user["id"] == user_id:
            if updated_user.email is not None:
                for existing_user in user_list:
                    if existing_user["email"] == updated_user.email and existing_user["id"] != user_id:
                        raise HTTPException(status_code=400, detail="Email already exists")
            user.update(updated_user.model_dump(exclude_unset=True))
            return user
    raise HTTPException(status_code=404, detail="User not found")

@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    for user in user_list:
        if user["id"] == user_id:
            user_list.remove(user)
            return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")