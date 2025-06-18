from typing import List, Optional
from sqlalchemy.orm import Session
from models.student import Student
from schemas.student import StudentCreate, StudentUpdate


def get_student_service():
    try:
        yield StudentService()
    finally:
        pass


class StudentService:
    
    def create_student(self, student_data: StudentCreate, db: Session) -> Student:
        """Tạo student mới"""
        db_student = Student(
            ho_ten=student_data.ho_ten,
            ngay_sinh=student_data.ngay_sinh,
            truong=student_data.truong
        )
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return db_student
    
    def get_student_by_id(self, student_id: int, db: Session) -> Optional[Student]:
        """Lấy student theo ID"""
        return db.query(Student).filter(Student.id == student_id).first()
    
    def get_all_students(self, db: Session, skip: int = 0, limit: int = 100) -> List[Student]:
        """Lấy danh sách tất cả students"""
        return db.query(Student).offset(skip).limit(limit).all()
    
    def update_student(self, student_id: int, student_data: StudentUpdate, db: Session) -> Optional[Student]:
        """Cập nhật thông tin student"""
        db_student = db.query(Student).filter(Student.id == student_id).first()
        if not db_student:
            return None
        
        # Chỉ cập nhật các field không None
        if student_data.ho_ten is not None:
            db_student.ho_ten = student_data.ho_ten
        if student_data.ngay_sinh is not None:
            db_student.ngay_sinh = student_data.ngay_sinh
        if student_data.truong is not None:
            db_student.truong = student_data.truong
        
        db.commit()
        db.refresh(db_student)
        return db_student
    
    def delete_student(self, student_id: int, db: Session) -> bool:
        """Xóa student"""
        db_student = db.query(Student).filter(Student.id == student_id).first()
        if not db_student:
            return False
        
        db.delete(db_student)
        db.commit()
        return True
