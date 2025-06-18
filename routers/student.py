from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT

from configs.database import get_db
from configs.authentication import get_current_user
from services.student_services import get_student_service, StudentService
from schemas.student import StudentCreate, StudentUpdate, StudentResponse

router = APIRouter(
    prefix="/api/students",
    tags=["students"],
)


def check_admin_permission(current_user: dict = Depends(get_current_user)):
    """Kiểm tra quyền admin cho các thao tác POST/PUT/DELETE"""
    if current_user.get("user_role") != "admin":
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới có quyền thực hiện thao tác này"
        )
    return current_user


@router.get("", status_code=HTTP_200_OK, response_model=List[StudentResponse])
async def get_all_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    student_service: StudentService = Depends(get_student_service),
    current_user: dict = Depends(get_current_user)
):
    students = student_service.get_all_students(db, skip=skip, limit=limit)
    return students


@router.get("/{student_id}", status_code=HTTP_200_OK, response_model=StudentResponse)
async def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    student_service: StudentService = Depends(get_student_service),
    current_user: dict = Depends(get_current_user)
):
    student = student_service.get_student_by_id(student_id, db)
    if not student:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Không tìm thấy student")
    return student


@router.post("", status_code=HTTP_201_CREATED, response_model=StudentResponse)
async def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db),
    student_service: StudentService = Depends(get_student_service),
    current_user: dict = Depends(check_admin_permission)
):
    student = student_service.create_student(student_data, db)
    return student


@router.put("/{student_id}", status_code=HTTP_200_OK, response_model=StudentResponse)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
    student_service: StudentService = Depends(get_student_service),
    current_user: dict = Depends(check_admin_permission)
):
    student = student_service.update_student(student_id, student_data, db)
    if not student:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Không tìm thấy student")
    return student


@router.delete("/{student_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    student_service: StudentService = Depends(get_student_service),
    current_user: dict = Depends(check_admin_permission)
):
    success = student_service.delete_student(student_id, db)
    if not success:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Không tìm thấy student")
    return {"message": "Xóa student thành công"}

