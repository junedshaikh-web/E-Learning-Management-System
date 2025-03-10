from flask import Blueprint, request, jsonify
from app import db
from app.models import Enrollment, User, Course
from app.schemas import EnrollmentSchema
from flask_jwt_extended import get_jwt_identity, jwt_required

enrollment_bp = Blueprint("enrollments", __name__)

enrollment_schema = EnrollmentSchema()
enrollments_schema = EnrollmentSchema(many=True)

def is_admin():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    return current_user and current_user.role == "admin"

def is_course_instructor(course_id):
    current_user_id = get_jwt_identity()
    course = Course.query.get(course_id)
    return course and course.instructor_id == current_user_id

@enrollment_bp.route("/", methods=["POST"])
@jwt_required()
def enroll_student():
    data = request.get_json()

    if not is_admin() and not is_course_instructor(data["course_id"]):
        return jsonify({"error": "Access denied. Admins and course instructors only."}), 403

    student = User.query.filter_by(id=data["student_id"], role="student").first()
    course = Course.query.get(data["course_id"])

    if not student or not course:
        return jsonify({"error": "Student or Course not found"}), 404

    if Enrollment.query.filter_by(student_id=student.id, course_id=course.id).first():
        return jsonify({"error": "Student already enrolled"}), 400

    new_enrollment = Enrollment(student_id=student.id, course_id=course.id)
    db.session.add(new_enrollment)
    db.session.commit()
    
    return enrollment_schema.jsonify(new_enrollment), 201

@enrollment_bp.route("/progress_up", methods=["PUT"])
@jwt_required()
def progress():

    current_user_id = get_jwt_identity()

    student = User.query.filter_by(id=current_user_id, role="student").first()
    if not student:
        return jsonify({"error": "Access denied. Only students can update their progress."}), 403
    
    data=request.get_json()
    course_id = data.get("course_id")
    completed_lessons = data.get("completed_lessons")

    if not all([ course_id, completed_lessons]):
        return jsonify({"error": "Missing required fields"}), 400
    
    course = Course.query.get(course_id)
    
    if not student:
        return jsonify({"error": "Student not found"}), 404
    if not course:
        return jsonify({"error": "Course not found"}), 404

    enrollment = Enrollment.query.filter_by(student_id=student.id, course_id=course.id).first()
    if not enrollment:
        return jsonify({"error": "Enrollment not found"}), 404

    if completed_lessons > course.lessons:
        return jsonify({"error": "Completed lessons cannot exceed total lessons"}), 400

    progress = (completed_lessons / course.lessons) * 100
    enrollment.progress = round(progress, 2)
    
    if enrollment.progress == 100:
        enrollment.completed = True

    db.session.commit()
    
    return jsonify({
        "message": "Progress updated successfully",
        "progress": enrollment.progress,
        "completed": enrollment.completed
    }), 200


@enrollment_bp.route("/view_progress/<int:id>/<int:course_id>", methods=["GET"])
@jwt_required()
def view_progress(id,course_id):

    if not is_admin() and not is_course_instructor(course_id):
        return jsonify({"error": "Access denied. Admins and course instructors only."}), 403

    enrollments = Enrollment.query.filter_by(student_id=id,course_id=course_id).all()

    if not enrollments:
        return jsonify({"message": "Student is not enrolled in any courses"}), 200

    progress_data = [
        {
            "course_id": enrollment.course.id,
            "course_name": enrollment.course.name,
            "progress": enrollment.progress,
            "completed": enrollment.completed
        }
        for enrollment in enrollments
    ]

    return jsonify({"student_id": id, "progress": progress_data}), 200
