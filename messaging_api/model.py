from datetime import datetime

from sqlalchemy import Boolean, Column, Computed, DateTime, ForeignKey, String, Text
from sqlalchemy.sql import false

from messaging_api import db


class User(db.Model):
    __tablename__ = 'user'
    __json_exclude__ = set(['datetime_added', 'datetime_updated'])
    ww_user_id = '48d11bef-5576-46fe-aa3b-73854f02a97b'
    gf_user_id = '7d2d5949-509d-4221-9940-ee3760067f0a'

    def __init__(self, user_id, first_name, last_name, primary_email, datetime_added=datetime.utcnow(), datetime_updated=datetime.utcnow()):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.primary_email = primary_email
        self.datetime_added = datetime_added
        self.datetime_updated = datetime_updated

    def __json__(self):
        json_exclude = getattr(self, '__json_exclude__', set())
        return {key: value for key, value in self.__dict__.items()
                # Do not serialize SQLAlchemy-internal attributes
                if not key.startswith('_')
                and key not in json_exclude}
    
    user_id = Column(String(36), primary_key=True, nullable=False)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    full_name = Column(String(128), Computed("first_name || ' ' || last_name"))
    primary_email = Column(String(128), nullable=False, unique=True)
    datetime_added = Column(DateTime, nullable=False)
    datetime_updated = Column(DateTime, nullable=False)

class Message(db.Model):
    __tablename__ = 'message'
    __json_exclude__ = set(['datetime_updated'])

    def __init__(self, message_id, sender_user_id, recipient_user_id, message_body, is_read=False, datetime_added=datetime.utcnow(), datetime_updated=datetime.utcnow()):
        self.message_id = message_id
        self.sender_user_id = sender_user_id
        self.recipient_user_id = recipient_user_id
        self.message_body = message_body
        self.is_read = is_read
        self.datetime_added = datetime_added
        self.datetime_updated = datetime_updated

    def __json__(self):
        json_exclude = getattr(self, '__json_exclude__', set())
        return {key: value for key, value in self.__dict__.items()
                # Do not serialize SQLAlchemy-internal attributes and any json excluded
                if not key.startswith('_')
                and key not in json_exclude}

    message_id = Column(String(36), primary_key=True, nullable=False)
    sender_user_id = Column(String(36), ForeignKey('user.user_id'), nullable=False)
    recipient_user_id = Column(String(36), ForeignKey('user.user_id'), nullable=False)
    message_body = Column(Text, nullable=False)
    is_read = Column(Boolean, nullable=False, server_default=false())
    datetime_added = Column(DateTime, nullable=False)
    datetime_updated = Column(DateTime, nullable=False)
