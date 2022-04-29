from email.headerregistry import MessageIDHeader
from uuid import uuid4

from flask import Blueprint, jsonify, make_response, request
from datetime import datetime, timedelta, date
from sqlalchemy import and_

from messaging_api import db
from .model import Message, User

message_bp = Blueprint('message', __name__, url_prefix=None)

@message_bp.route('/message', methods=["POST"])
def create_message():
    """
        required JSON keys: sender_user_id, recipient_user_id, message_body
    """
    if json_body := request.get_json():
        if sender := db.session.query(User).filter(User.user_id == json_body['sender_user_id']).first():
            if recipient := db.session.query(User).filter(User.user_id == json_body['recipient_user_id']).first():
                if not json_body['message_body']:
                    return make_response(jsonify({"message": "Empty message body. Please fill out message body"}), 200)

                if len(json_body['message_body']) > 500: # Shorter messages only
                    return make_response(jsonify({"message": f"Message body character count exceeded 1000 characters. Please reduce message body size"}), 200)

                new_message = Message(
                    message_id=str(uuid4()),
                    sender_user_id=json_body['sender_user_id'],
                    recipient_user_id=json_body['recipient_user_id'],
                    message_body=json_body['message_body']
                )
                db.session.add(new_message)
                db.session.commit()
                return make_response(jsonify({"message": "OK", "message_id": new_message.message_id}), 201)
            return make_response(jsonify({"message": f"Recipient with {json_body['recipient_user_id']} user_id not found"}), 200)
        return make_response(jsonify({"message": f"Sender with {json_body['sender_user_id']} user_id not found"}), 200)
    return make_response(jsonify({"message": "Missing JSON body"}), 422)

@message_bp.route('/message', methods=["GET"])
def retrieve_message():
    """
        required query params: message_id
    """
    if message_id := request.args.get('message_id'):
        if message := db.session.query(Message).filter(Message.user_id == message_id).first():
            return make_response(jsonify({"user": message.__json__()}))
        return make_response(jsonify({"message": f"Message: {message_id} not found"}), 200)
    return make_response(jsonify({"message": "Missing message_id query param"}), 400)

@message_bp.route('/messages', methods=["GET"])
def retrieve_messages():
    """
        required query params: sender_user_id (optional, string, required if recipient_user_id provided),
                               recipient_user_id (optional, string, required if recipient_user_id provided),
                               since_date (optional, string, format: MM/dd/yyyy, example: 04/01/2022),
                               limit (optional, integer, defaults to 100)
    """
    sender_user_id = request.args.get('sender_user_id', default=None)
    recipient_user_id = request.args.get('recipient_user_id', default=None)

    limit = request.args.get('limit', default=100)

    since_date = request.args.get('since_date', default=datetime.utcnow() - timedelta(days=30))
    if isinstance(since_date, str):
        since_date = datetime.strptime(since_date, "%m/%d/%Y")

    ### Note: if auth was implemented, recipient_user_id, and all it's logic, ###
    ### would not be necessary as the auth process would determine who the recipient is, i.e. the user making the request. ###
    ### For example, if JWT auth was used, on each request, we would know the user making the request. Users can only see messages where they are the recipient. ###

    ### Furthermore, if our app did allow messages to self, then we would also be able to skip more logic. I am building with the assumption that this is not allowed ###

    if sender_user_id and not recipient_user_id:
        return make_response(jsonify({"message": f"Please provide a recipient_user_id query param"}), 200)
    elif not sender_user_id and recipient_user_id:
        return make_response(jsonify({"message": f"Please provide a sender_user_id query param"}), 200)
    elif (sender_user_id and recipient_user_id) and (sender_user_id == recipient_user_id): # Check that sender is not also recipient
        return make_response(jsonify({"message": f"Please provide unique sender_user_id and recipient_user_id query params"}), 200)
    elif not sender_user_id and not recipient_user_id:
        # Retrieve all messages if neither sender nor recipient provided
        messages = db.session.query(Message).filter(Message.datetime_added >= since_date).order_by(Message.datetime_added.desc()).limit(limit).all()
    else:
        if not db.session.query(User).filter(User.user_id == sender_user_id).first(): # Check that sender user exists
            return make_response(jsonify({"message": f"Sender user: {sender_user_id} not found"}), 200)

        if recipient := db.session.query(User).filter(User.user_id == recipient_user_id).first(): # Check that recipient user exists
            return make_response(jsonify({"message": f"Recipient user: {recipient_user_id} not found"}), 200)

        # Retrieve messages for a recipient from a specific sender
        messages = db.session.query(Message).filter(and_(
            Message.sender_user_id == sender_user_id, Message.recipient_user_id == recipient_user_id, Message.datetime_added >= since_date
        )).order_by(Message.datetime_added.desc()).limit(limit).all()

    # Finally
    if messages:
        return make_response(jsonify({"messages": [message.__json__() for message in messages]}))
    return make_response(jsonify({"message": "No messages found"}), 200)
