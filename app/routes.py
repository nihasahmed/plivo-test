from flask import request, jsonify, current_app
from . import db
from .models import Message
from .schemas import message_schema, messages_schema
import uuid


def register_routes(app):
    @app.route('/get/messages/<account_id>', methods=['GET'])
    def get_messages(account_id):
        current_app.logger.info(f'Retrieving messages for account_id: {account_id}')
        try:
            messages = Message.query.filter_by(account_id=account_id).all()
            return messages_schema.jsonify(messages)
        except Exception as e:
            current_app.logger.error(f'Error retrieving messages for account_id {account_id}: {e}')
            return jsonify({'error': 'An error occurred'}), 500

    @app.route('/create', methods=['POST'])
    def create_message():
        data = request.get_json()
        current_app.logger.info(f'Creating message with data: {data}')
        try:
            new_message = Message(
                account_id=data['account_id'],
                message_id=str(uuid.uuid4()),
                sender_number=data['sender_number'],
                receiver_number=data['receiver_number']
            )
            db.session.add(new_message)
            db.session.commit()
            current_app.logger.info(f'Message created with message_id: {new_message.message_id}')
            return message_schema.jsonify(new_message)
        except Exception as e:
            current_app.logger.error(f'Error creating message: {e}')
            return jsonify({'error': 'An error occurred'}), 500

    @app.route('/search', methods=['GET'])
    def search_messages():
        query = Message.query
        current_app.logger.info(f'Searching messages with params: {request.args}')
        try:
            if 'message_id' in request.args:
                query = query.filter(Message.message_id.in_(request.args.get("message_id").split(',')))
            if 'sender_number' in request.args:
                query = query.filter(Message.sender_number.in_(request.args.get("sender_number").split(',')))
            if 'receiver_number' in request.args:
                query = query.filter(Message.receiver_number.in_(request.args.get("receiver_number").split(',')))
            if 'account_id' in request.args:
                query = query.filter(Message.account_id==request.args.get("account_id"))
            messages = query.all()
            return messages_schema.jsonify(messages)
        except Exception as e:
            current_app.logger.error(f'Error searching messages: {e}')
            return jsonify({'error': 'An error occurred'}), 500

