from flask import Blueprint, request, jsonify
from app import db
from app.decorators import admin_or_instructor_owns_course_required
from app.models import Course, User
from app.schemas import CourseSchema
from flask_jwt_extended import jwt_required

course_bp = Blueprint("courses", __name__)

course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)

@course_bp.route("/", methods=["POST"])
@jwt_required()
def create_course():
    data = request.get_json()
    instructor = User.query.get(data["instructor_id"])

    if not instructor:
        return jsonify({"error": "Instructor not found"}), 404

    new_course = Course(
        name=data["name"],
        description=data["description"],
        duration=data["duration"],
        lessons=data["lessons"],
        instructor_id=data["instructor_id"],
    )
    db.session.add(new_course)
    db.session.commit()
    return course_schema.dump(new_course), 201

@course_bp.route("/", methods=["GET"])
@admin_or_instructor_owns_course_required
def get_courses():
    courses = Course.query.filter_by(is_active=True).all()
    return courses_schema.jsonify(courses), 200

@course_bp.route("/<int:id>", methods=["GET"])
@admin_or_instructor_owns_course_required
def get_course(id):
    course = Course.query.get(id)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    return course_schema.jsonify(course), 200

@course_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
@admin_or_instructor_owns_course_required
def update_course(id):
    course = Course.query.get(id)
    if not course:
        return jsonify({"error": "Course not found"}), 404

    data = request.get_json()
    course.name = data.get("name", course.name)
    course.description = data.get("description", course.description)
    course.duration = data.get("duration", course.duration)
    db.session.commit()
    return course_schema.jsonify(course), 200

@course_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
@admin_or_instructor_owns_course_required
def delete_course(id):
    course = Course.query.get(id)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    db.session.delete(course)
    db.session.commit()
    return jsonify({"message": "Course deleted successfully"}), 200
