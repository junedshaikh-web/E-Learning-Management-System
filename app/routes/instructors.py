from flask import Blueprint, request, jsonify
from app import db
from app.models import User
from app.schemas import InstructorSchema
from flask_jwt_extended import get_jwt_identity, jwt_required

instructor_bp = Blueprint("instructors", __name__)

instructor_schema = InstructorSchema()
instructors_schema = InstructorSchema(many=True)

def is_admin():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    return current_user and current_user.role == "admin"

@instructor_bp.route("/make_instructor", methods=["POST"])
@jwt_required()
def create_instructor():
    if not is_admin():
        return jsonify({"error": "Access denied. Admins only."}), 403

    data = request.get_json()

    if not data or "email" not in data or "name" not in data or "password" not in data:
        return jsonify({"error": "Name, email, and password are required"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 400

    new_instructor = User(
        name=data["name"],
        email=data["email"],
        role="instructor",
        contact=data.get("contact"),
        bio=data.get("bio"),
    )
    new_instructor.password = data["password"]

    db.session.add(new_instructor)
    db.session.commit()

    return jsonify({"message": "Instructor created successfully!"}), 201

@instructor_bp.route("/instructor_admin/<int:id>", methods=["PUT"])
@jwt_required()
def instructor_to_admin(id):
    if not is_admin():
        return jsonify({"error": "Access denied. Admins only."}), 403

    instructor = User.query.filter_by(id=id, role="instructor").first()

    if not instructor:
        return jsonify({"error": "Instructor not found"}), 404

    instructor.role = "admin"
    db.session.commit()

    return jsonify({"message": "Instructor promoted to admin successfully!"}), 200


@instructor_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def update_instructor(id):

    if not is_admin():
        return jsonify({"error": "Access denied. Admins only."}), 403

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

@instructor_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def get_instructor(id):
    if not is_admin():
        return jsonify({"error": "Access denied. Admins only."}), 403
    
    instructor = User.query.filter_by(id=id, role="instructor").first()
    if not instructor:
        return jsonify({"error": "Instructor not found"}), 404
    
    return instructor_schema.jsonify(instructor), 200

@instructor_bp.route("/", methods=["GET"])
@jwt_required()
def get_instructors():

    if not is_admin():
        return jsonify({"error": "Access denied. Admins only."}), 403
    
    instructors = User.query.filter_by(role="instructor").all()
    return instructors_schema.jsonify(instructors), 200

@instructor_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_instructor(id):
    if not is_admin():
        return jsonify({"error": "Access denied. Admins only."}), 403
    
    instructor = User.query.filter_by(id=id, role="instructor").first()
    if not instructor:
        return jsonify({"error": "Instructor not found"}), 404

    db.session.delete(instructor)
    db.session.commit()
    return jsonify({"message": "Instructor deleted successfully"}), 200
