from flask import Blueprint, request, jsonify
from app import db
from app.decorators import admin_or_instructor_owns_course_required
from app.models import User
from app.schemas import InstructorSchema
from flask_jwt_extended import get_jwt_identity, jwt_required

instructor_bp = Blueprint("instructors", __name__)

instructor_schema = InstructorSchema()
instructors_schema = InstructorSchema(many=True)

# Update instructor details
@instructor_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def update_instructor(id):
    instructor = User.query.filter_by(id=id, role="instructor").first()

    if not instructor:
        return jsonify({"error": "Instructor not found"}), 404

    data = request.get_json()

    if "email" in data:
        existing_user = User.query.filter_by(email=data["email"]).first()
        if existing_user and existing_user.id != id:
            return jsonify({"error": "Email is already in use"}), 400
        instructor.email = data["email"]

    if "name" in data:
        instructor.name = data["name"]
    if "bio" in data:
        instructor.bio = data.get("bio")
    if "contact" in data:
        instructor.contact = data.get("contact")

    db.session.commit()
    return instructor_schema.jsonify(instructor), 200

# Get all instructors
@instructor_bp.route("/", methods=["GET"])
def get_instructors():
    instructors = User.query.filter_by(role="instructor").all()
    return instructors_schema.jsonify(instructors), 200

# Delete instructor
@instructor_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
@admin_or_instructor_owns_course_required
def delete_instructor(id):
    instructor = User.query.filter_by(id=id, role="instructor").first()
    if not instructor:
        return jsonify({"error": "Instructor not found"}), 404

    db.session.delete(instructor)
    db.session.commit()
    return jsonify({"message": "Instructor deleted successfully"}), 200
