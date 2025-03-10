from flask import Blueprint, request, jsonify
from app import db
from app.models import Course, Enrollment, User
from app.schemas import CourseSchema
from flask_jwt_extended import get_jwt_identity, jwt_required

course_bp = Blueprint("courses", __name__)

course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)

@course_bp.route("/", methods=["POST"])
@jwt_required()
def create_course():
    current_user = User.query.get(get_jwt_identity())

    if not current_user or current_user.role != "instructor":
        return jsonify({"error": "Access denied. Only instructors can create courses."}), 403
    
    data = request.get_json()

    if data.get("instructor_id") != current_user.id:
        return jsonify({"error": "You can only create courses under your own name."}), 403

    new_course = Course(
        name=data["name"],
        description=data["description"],
        duration=data["duration"],
        lessons=data["lessons"],
        instructor_id=current_user.id,
    )
    db.session.add(new_course)
    db.session.commit()
    return course_schema.dump(new_course), 201


@course_bp.route("/", methods=["GET"])
@jwt_required()
def get_courses():
    current_user = User.query.get(get_jwt_identity())

    if not current_user or current_user.role != "admin":
        return jsonify({"error": "Access denied. Only admins can view all courses."}), 403

    courses = Course.query.filter_by(is_active=True).all()
    return courses_schema.jsonify(courses), 200


@course_bp.route("/instructor", methods=["GET"])
@jwt_required()
def get_instructor_courses():
    current_user = User.query.get(get_jwt_identity())

    if not current_user or current_user.role not in ["admin", "instructor"]:
        return jsonify({"error": "Access denied. Only instructors and admins can view courses."}), 403

    if current_user.role == "instructor":
        courses = Course.query.filter_by(instructor_id=current_user.id, is_active=True).all()
    else: 
        courses = Course.query.filter_by(is_active=True).all()

    return courses_schema.jsonify(courses), 200


@course_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def get_course(id):
    current_user = User.query.get(get_jwt_identity())

    if not current_user or current_user.role not in ["admin", "instructor"]:
        return jsonify({"error": "Access denied. Only instructors and admins can view courses."}), 403
    
    course = Course.query.get(id)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    return course_schema.jsonify(course), 200

@course_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def update_course(id):
    current_user = User.query.get(get_jwt_identity())

    if not current_user or current_user.role not in ["admin", "instructor"]:
        return jsonify({"error": "Access denied. Only instructors and admins can view courses."}), 403
    
    course = Course.query.get(id)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    
    if current_user.role == "instructor" and course.instructor_id != current_user.id:
        return jsonify({"error": "Access denied. Instructors can only update their own courses."}), 403

    data = request.get_json()
    course.name = data.get("name", course.name)
    course.description = data.get("description", course.description)
    course.duration = data.get("duration", course.duration)
    db.session.commit()
    return course_schema.jsonify(course), 200

@course_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_course(id):
    current_user = User.query.get(get_jwt_identity())

    if not current_user or current_user.role != "admin":
        return jsonify({"error": "Access denied. Only admins can delete courses."}), 403

    course = Course.query.get(id)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    
    Enrollment.query.filter_by(course_id=id).delete()
    db.session.commit()

    db.session.delete(course)
    db.session.commit()

    return jsonify({"message": "Course and all related enrollments deleted successfully"}), 200


