from uuid import uuid4

from flask import Blueprint, jsonify, make_response, request

from messaging_api import db
from .model import Message, User

user_bp = Blueprint('user', __name__, url_prefix=None)

@user_bp.route('/user', methods=["POST"])
def create_user():
    """
        required JSON keys: first_name, last_name, primary_email
    """
    if json_body := request.get_json():
        if existing_user := db.session.query(User).filter(User.primary_email == json_body['primary_email']).first():
            return make_response(jsonify({"message": f"User with email {json_body['primary_email']} already exists. Please enter a different email."}), 409)
        new_user = User(
            user_id=str(uuid4()),
            first_name=json_body['first_name'],
            last_name=json_body['last_name'],
            primary_email=json_body['primary_email']
        )
        db.session.add(new_user)
        db.session.commit()
        return make_response(jsonify({"message": "OK", "user_id": new_user.user_id}), 201)
    return make_response(jsonify({"message": "Missing JSON body"}), 422)

@user_bp.route('/user', methods=["GET"])
def get_user():
    """
        required query params: user_id
    """
    if user_id := request.args.get('user_id'):
        if user := db.session.query(User).filter(User.user_id == user_id).first():
            return make_response(jsonify({"user": user.__json__()}))
        return make_response(jsonify({"message": f"User: {user_id} not found"}), 200)
    return make_response(jsonify({"message": "Missing user_id query param"}), 400)

@user_bp.route('/users', methods=["GET"])
def get_users():
    """
        required query params: none
    """
    if users := db.session.query(User).all():
        return make_response(jsonify({"users": [user.__json__() for user in users]}))
    return make_response(jsonify({"message": "No users found"}), 200)
