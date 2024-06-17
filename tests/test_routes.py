import pytest
from app import create_app, db
from app.models import Message

@pytest.fixture
def client():
    app = create_app(testing=True)
    
    import os
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

def test_create_message(client):
    response = client.post('/create', json={
        'account_id': '1',
        'sender_number': '1234567890',
        'receiver_number': '0987654321'
    })
    assert response.status_code == 200
    assert response.json['account_id'] == '1'

def test_get_messages(client):
    client.post('/create', json={
        'account_id': '1',
        'sender_number': '1234567890',
        'receiver_number': '0987654321'
    })
    response = client.get('/get/messages/1')
    assert response.status_code == 200
    assert len(response.json) == 1

def test_search_messages(client):
    client.post('/create', json={
        'account_id': '1',
        'sender_number': '1234567890',
        'receiver_number': '0987654321'
    })
    response = client.get('/search?sender_number=1234567890&account_id=1')
    assert response.status_code == 200
    assert len(response.json) == 1
