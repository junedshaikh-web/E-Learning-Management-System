from flask import Blueprint, request, jsonify
from app import db
from app.decorators import admin_or_instructor_owns_course_required
from app.models import User, Enrollment, Course
from app.schemas import UserSchema
from flask_jwt_extended import jwt_required
from werkzeug.security import generate_password_hash

student_bp = Blueprint("students", __name__)

student_schema = UserSchema()
students_schema = UserSchema(many=True)

@student_bp.route("/", methods=["POST"])
def create_student():
    data = request.get_json()

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 400

    hashed_password = generate_password_hash(data["password"])

    new_student = User(
        name=data["name"],
        email=data["email"],
        contact=data.get("contact"),
        password=hashed_password,
        role="student"  
    )

    db.session.add(new_student)
    db.session.commit()
    return student_schema.jsonify(new_student), 201

@student_bp.route("/", methods=["GET"])
@jwt_required()
def get_students():
    students = User.query.filter_by(role="student",is_active=True).all()  
    return students_schema.jsonify(students), 200

@student_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def get_student(id):
    student = User.query.filter_by(id=id, role="student", is_active = True).first()  
    if not student:
        return jsonify({"error": "Student not found"}), 404

    enrollments = Enrollment.query.filter_by(student_id=id,is_active = True).all()
    courses = [
        {
            "course_id": e.course.id,
            "course_name": e.course.name,
            "instructor": e.course.instructor.name
        }
        for e in enrollments
    ]

    student_data = {
        "student_id": student.id,
        "name": student.name,
        "email": student.email,
        "contact": student.contact,
        "enrolled_courses": courses
    }

    return jsonify(student_data), 200   


@student_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
@admin_or_instructor_owns_course_required
def update_student(id):
    student = User.query.filter_by(id=id, role="student",is_active=True).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json()

    if "name" in data:
        student.name = data["name"]
    if "email" in data:
        if User.query.filter(User.email == data["email"], User.id != id).first():
            return jsonify({"error": "Email already in use"}), 400
        student.email = data["email"]
    if "contact" in data:
        student.contact = data["contact"]
    if "password" in data:
        student.password = generate_password_hash(data["password"]) 

    db.session.commit()
    return student_schema.jsonify(student), 200


@student_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
@admin_or_instructor_owns_course_required
def delete_student(id):
    student = User.query.filter_by(id=id, role="student").first()
    if not student:
        return jsonify({"error": "Student not found"}), 404

    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student deleted successfully"}), 200
