import json
from app import app, db, User

def setup_module(module):
    with app.app_context():
        db.create_all()

def test_register_and_login():
    client = app.test_client()
    r = client.post('/register', json={'email':'u1@example.com','password':'pw'})
    assert r.status_code in (201, 409)  # allow rerun
    r = client.post('/login', json={'email':'u1@example.com','password':'pw'})
    assert r.status_code == 200
    token = r.get_json()['access_token']
    assert isinstance(token, str)
