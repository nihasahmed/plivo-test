from . import db
import uuid
import random


rd = random.Random()

class Message(db.Model):
    account_id = db.Column(db.String(50), nullable=False)
    message_id = db.Column(db.String(36), default=uuid.uuid4, unique=True, nullable=False, primary_key=True)
    sender_number = db.Column(db.String(15), nullable=False)
    receiver_number = db.Column(db.String(15), nullable=False)
