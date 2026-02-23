# Part 6

from sqlalchemy import (
    MetaData, Table, Column, 
    Integer, String, Numeric, DateTime, Enum,
    ForeignKey, ForeignKeyConstraint, Unicode, UnicodeText,
    create_engine, select, inspect
)

from sqlalchemy.orm import (
    declarative_base, relationship, Session
)

import os

if os.path.exists("orm.db"):
    os.remove("orm.db")

engine = create_engine("sqlite:///orm.db")
#engine = create_engine("sqlite:///orm.db", echo=True)

Base = declarative_base()

enrollments = Table(
    "enrollments",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.student_id")),
    Column("course_id", Integer, ForeignKey("courses.course_id"))
)

class Student(Base):
    __tablename__ = "students"
    
    student_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    
    courses = relationship("Course", secondary=enrollments, back_populates="students")
    
    def __repr__(self):
        return f"Student(id={self.student_id}, name={self.name})"

class Course(Base):
    __tablename__ = "courses"
    
    course_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    
    students = relationship("Student", secondary=enrollments, back_populates="courses")
    
    def __repr__(self):
        return f"Course(id={self.course_id}, title={self.title})"

Base.metadata.create_all(engine)

with Session(engine) as session:
    student1 = Student(student_id=1, name="Yuichi")
    student2 = Student(student_id=2, name="Tatsunari")
    student3 = Student(student_id=3, name="lee")
    
    course1 = Course(course_id=1, title="Mathematics")
    course2 = Course(course_id=2, title="English")
    
    student1.courses.append(course1)  # Yuichi -> Math
    student1.courses.append(course2)  # Yuichi -> English
    student2.courses.append(course1)  # Tatsunari -> Math
    student3.courses.append(course2)  # lee -> English

    session.add_all([student1, student2, student3, course1, course2])
    session.commit()
    
    print("\nAll Students:")
    all_students = session.query(Student).all()
    for s in all_students:
        print(s)
    
    print("\nCourses for Yuichi (student.courses):")
    yuichi = session.query(Student).filter_by(name="Yuichi").first()
    for course in yuichi.courses:
        print(course)
    
    print("\nStudents in Math (course.students):")
    math = session.query(Course).filter_by(title="Mathematics").first()
    for student in math.students:
        print(student)