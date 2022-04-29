import json
import os
from datetime import datetime, timedelta
from uuid import uuid4

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

db = SQLAlchemy()

# create and configure the app
def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    # Set db url
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/ge.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize flask-sqlalchemy db 
    db.init_app(app)

    # Import blueprints and register them
    from . import message as Message
    from . import user as User
    app.register_blueprint(User.user_bp)
    app.register_blueprint(Message.message_bp)

    # Drop existing tables if exist and then create tables
    @app.before_first_request
    def create_tables():
        db.drop_all()
        db.create_all()

        # Add default data
        if os.getenv('IS_DEFAULT_DATA', None):
            # Add default users
            from .model import Message, User
            walter = User(User.ww_user_id,'Walter','White','heisenberg@graymatter.com')
            gustavo = User(User.gf_user_id, 'Gustavo', 'Fring', 'gus.fring@lospolloshermanos.com')
            db.session.add(walter)
            db.session.add(gustavo)

            # Add default messages
            import random

            from .sample_data import walter_white_quotes
            user_id_list = [walter.user_id, gustavo.user_id]
            ### These filler/default messages are inserted to test 2 qualities of the api: ###
            ### "By default, only messages from the last 30 days should be returned. Additionally,there should be a limit of 100 messages in a response" ###
            for i in range(200):
                sender_user_id = random.choices(user_id_list, k=1)[0]
                db.session.add(Message(
                    str(uuid4()),
                    sender_user_id=sender_user_id,
                    recipient_user_id=user_id_list[0] if user_id_list[0] != sender_user_id else user_id_list[1],
                    message_body="Filler message",
                    datetime_added=datetime.utcnow() - timedelta(days=220 - i),
                    datetime_updated=datetime.utcnow() - timedelta(days=220 - i)
                ))
                
            db.session.add(Message(
                str(uuid4()),
                sender_user_id=walter.user_id,
                recipient_user_id=gustavo.user_id,
                message_body="Hey Gus, here are some of my best quotes. Gonna send them over the next 20 days. Enjoy!",
                datetime_added=datetime.utcnow() - timedelta(days=21),
                datetime_updated=datetime.utcnow() - timedelta(days=21)
            ))
            for i, quote in enumerate(walter_white_quotes):
                db.session.add(Message(
                    str(uuid4()),
                    sender_user_id=walter.user_id,
                    recipient_user_id=gustavo.user_id,
                    message_body=quote,
                    datetime_added=datetime.utcnow() - timedelta(days=20 - i),
                    datetime_updated=datetime.utcnow() - timedelta(days=20 - i)
                ))

            db.session.commit()

    return app
