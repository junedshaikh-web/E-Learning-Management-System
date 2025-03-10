from flask import Blueprint, request, jsonify, make_response,json
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    unset_jwt_cookies,
    set_access_cookies,
    set_refresh_cookies
)
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User

auth = Blueprint("auth", __name__)

def validate_contact(contact):
    return contact.isdigit() and len(contact) == 10

@auth.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing required fields"}), 400

    if not data.get("email") or not data.get("password") or not data.get("confirm_password"):
            return jsonify({"error": "Email, password, and confirm_password are required"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 400
    
    if data["password"] != data["confirm_password"]:
        return jsonify({"error": "Passwords do not match"}), 400
    
    contact = data.get("contact")
    if contact and not validate_contact(contact):
        return jsonify({"error": "Invalid contact number. Must be exactly 10 digits."}), 400

    new_user = User(
            name=data.get("name"),
            email=data["email"],
            contact=data.get("contact"),
            bio=data.get("bio")
    )
    new_user.password = data['password']
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": f"student registered successfully!"}), 201


@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    
    password = data.get('password')

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    role =  user.role  

    access_token = create_access_token(identity=str(user.id), additional_claims={"role": role})
    refresh_token = create_refresh_token(identity=user.id)

    response = jsonify({"message": "Login successful", "role": role})

    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)

    return response, 200


@auth.route("/logout", methods=["POST"])
@jwt_required()
def logout():

    response = jsonify({"message": "Logout successful"})
    
    unset_jwt_cookies(response) 

    return response, 200


@auth.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)

    response = jsonify({"message": "Token refreshed"})
    set_access_cookies(response, new_access_token)

    return response, 200


@auth.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    identity = get_jwt_identity()
    return jsonify({"message": "Access granted", "user": identity}), 200
