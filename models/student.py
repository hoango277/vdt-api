from sqlalchemy import Column, Integer, String, Date
from configs.database import Base


class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ho_ten = Column(String(100), nullable=False)
    ngay_sinh = Column(Date, nullable=False)
    truong = Column(String(255), nullable=False)