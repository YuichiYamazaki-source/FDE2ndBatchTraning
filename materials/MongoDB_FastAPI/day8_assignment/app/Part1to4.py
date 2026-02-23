from sqlalchemy import (
    MetaData, Table, Column, 
    Integer, String, Numeric, DateTime, Enum,
    ForeignKey, ForeignKeyConstraint, Unicode, UnicodeText,
    create_engine, select, inspect
)

import os

# part1

if os.path.exists("some.db"):
    os.remove("some.db")

engine = create_engine("sqlite:///some.db")
#engine = create_engine("sqlite:///some.db", echo=True)

metadata = MetaData()

#Q. Comment in code: which part is DBAPI driver and which is SQLAlchemy wrapper (based on what you taught in DBAPI vs Engine)
#A: DBAPI Driver is sqlite3 and wrapper is Engine. 
# DBAPI Driver is communicates with the DB diretly. So it is nearly DB.
# Engine is like a translator in my understanding, it includes connection pooling and dialect.
# SQL DB has a lot of kinds and each DB type has own grammer. So, if I can't use SQLAlchemy, I should remember all SQL DB grammer.
# But If I can use SQLAlchemy, Engine translate the Object to SQL Automatically, so I can only use python.
# connection pooling and Dialect is a part of it.I think Engine is important in SQLAlchemy.

# part2
students_table = Table(
    "students",
    metadata,
    Column("student_id", Integer, primary_key=True),
    Column("name", String, nullable=False)
)

courses_table = Table(
    "courses",
    metadata,
    Column("course_id", Integer, primary_key=True),
    Column("title", String, nullable=False)
)

enrollments_Table = Table(
    "enrollments",
    metadata,
    Column("student_id", Integer, ForeignKey("students.student_id")),
    Column("course_id", Integer, ForeignKey("courses.course_id"))
)

#Part3
metadata.create_all(engine)

with engine.begin() as conn:
    conn.execute(
        students_table.insert().values([
            {"student_id" : 1, "name": "Yuichi"},
            {"student_id" : 2, "name": "Tatsunari"},
            {"student_id" : 3, "name": "lee"}
            ]
        )
    )
    conn.execute(
        courses_table.insert().values([
            {"course_id" : 1, "title" : "Mathmatic"},
            {"course_id" : 2, "title" : "English"}
        ])
    )
    conn.execute(
        enrollments_Table.insert().values([
            {"student_id" : 1, "course_id": "1"},
            {"student_id" : 1, "course_id": "2"},
            {"student_id" : 2, "course_id": "1"},
            {"student_id" : 3, "course_id": "2"}
        ])
    )

with engine.begin() as conn:
    all_students = conn.execute(select(students_table))
    print("All Students:")
    for row in all_students:
        print(row)
    
    student_courses = conn.execute(
        select(courses_table)
        .select_from(
            courses_table
            .join(enrollments_Table, courses_table.c.course_id == enrollments_Table.c.course_id)
        )
        .where(enrollments_Table.c.student_id == 1)
    )
    print("\nCourses in student_id 1:")
    for row in student_courses:
        print(row)
    
    course_students = conn.execute(
        select(students_table)
        .select_from(
            students_table
            .join(enrollments_Table, students_table.c.student_id == enrollments_Table.c.student_id)
        )
        .where(enrollments_Table.c.course_id == 1)
    )
    print("\nStudents in course_id 1:")
    for row in course_students:
        print(row)

# Part4
inspector = inspect(engine)

print("All Table Names:")
table_names = inspector.get_table_names()
print(table_names)

print("\nColumns for Each Table:")
for table_name in table_names:
    print(f"\nTable: {table_name}")
    columns = inspector.get_columns(table_name)
    for col in columns:
        print(f"  - {col['name']}, Type: {col['type']}, Nullable: {col['nullable']}")

print("\nForeign Keys for enrollments:")
foreign_keys = inspector.get_foreign_keys("enrollments")
for fk in foreign_keys:
    print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

#Q. “What can Inspector do that MetaData cannot, and vice versa?”
#(Reinforces: Inspector is read‑only, MetaData can be used to build
#expressions and participate in transactions.)
 
# A. 
# What Inspector CAN do that MetaData CANNOT:

# Get detailed database info without loading tables into Python objects
# List indexes, check constraints, unique constraints
# Inspect database structure without affecting anything
# Lightweight - just reads raw info as dictionaries

# What MetaData CAN do that Inspector CANNOT:

# Create, Update, Drop 
# Build SQL expressions (INSERT, SELECT, UPDATE, DELETE)
# Participate in transactions
# Define schema in code

# Part 5
reflected_metadata = MetaData()

reflected_metadata.reflect(bind=engine)

students_reflected = reflected_metadata.tables["students"]
enrollments_reflected = reflected_metadata.tables["enrollments"]
courses_reflected = reflected_metadata.tables["courses"]

with engine.begin() as conn:
    print("\nAll Students (using reflected table):")
    result = conn.execute(select(students_reflected))
    for row in result:
        print(row)
    
    print("\nAll Enrollments (join reflected tables):")
    result = conn.execute(
        select(
            students_reflected.c.student_id,
            students_reflected.c.name,
            enrollments_reflected.c.course_id
        )
        .select_from(
            students_reflected.join(
                enrollments_reflected,
                students_reflected.c.student_id == enrollments_reflected.c.student_id
            )
        )
    )
    for row in result:
        print(row)

