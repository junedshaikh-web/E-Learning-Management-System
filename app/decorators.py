from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from functools import wraps
from app.models import User, Course

def admin_or_instructor_owns_course_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))

        if not user:
            return jsonify({"error": "User not found"}), 404

        if user.is_admin or user.role == "admin": 
            return fn(*args, **kwargs)

        if user.role != "instructor":  
            return jsonify({"error": "Access restricted to instructors and admins"}), 403

        course_id = kwargs.get("id")  
        if not course_id:
            return jsonify({"error": "Course ID is required"}), 400

        course = Course.query.get(course_id)
        if not course:
            return jsonify({"error": "Course not found"}), 404

        if course.instructor_id != user.id:  
            return jsonify({"error": "You are not authorized to manage this course"}), 403

        return fn(*args, **kwargs)  

    return wrapper
