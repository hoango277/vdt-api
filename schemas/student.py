from datetime import date
from pydantic import BaseModel, Field
from typing import Optional


class StudentCreate(BaseModel):
    ho_ten: str = Field(..., min_length=1, max_length=100, description="Họ và tên")
    ngay_sinh: date = Field(..., description="Ngày sinh")
    truong: str = Field(..., description="Tên trường đại học")


class StudentUpdate(BaseModel):
    ho_ten: Optional[str] = Field(None, min_length=1, max_length=100, description="Họ và tên")
    ngay_sinh: Optional[date] = Field(None, description="Ngày sinh")
    truong: Optional[str] = Field(None, description="Tên trường đại học")


class StudentResponse(BaseModel):
    id: int
    ho_ten: str
    ngay_sinh: date
    truong: str

    class Config:
        from_attributes = True 