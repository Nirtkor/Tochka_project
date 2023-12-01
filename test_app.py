# test_app.py

from flask.testing import FlaskClient
import pytest
from app import app, db, User, Roles, Product, Reservation

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@localhost:5432/postgres'
    client = app.test_client()

    with app.app_context():
        db.create_all()

    yield client

def test_index(client: FlaskClient):
    response = client.get('/')
    assert response.status_code == 200

def test_route_signup(client: FlaskClient):
    response = client.get('/signup')
    assert response.status_code == 200

def test_route_signin(client: FlaskClient):
    response = client.get('/login')
    assert response.status_code == 200

def test_route_contact(client: FlaskClient):
    response = client.get('/#contact')
    assert response.status_code == 200

def test_route_intro(client: FlaskClient):
    response = client.get('/#intro')
    assert response.status_code == 200

def test_route_about(client: FlaskClient):
    response = client.get('/#about')
    assert response.status_code == 200

def test_route_work(client: FlaskClient):
    response = client.get('/#work')
    assert response.status_code == 200

def test_signup_functionality(client: FlaskClient):
    response = client.post('/signup', data=dict(
        name='testuser',
        email='test@example.com',
        password='testpassword',
        role_id=1
    ), follow_redirects=True)

    assert response.status_code == 200

def test_login(client: FlaskClient):
    response = client.post('/login', data={'email': 'test@example.com', 'password': 'testpassword'})
    assert response.status_code == 200

def test_admin(client: FlaskClient):
    client.post('/login', data={'email': 'test@example.com', 'password': 'testpassword'})
    response = client.get('/admin')
    assert response.status_code == 308

def test_moderating(client: FlaskClient):
    try:
        client.post('/signup', data=dict(
            name='testuser4',
            email='test4@example.com',
            password='testpassword4',
            role_id=2
        ), follow_redirects=True)
    except:
        pass
    client.post('/login', data={'email': 'test4@example.com', 'password': 'testpassword4'})
    response = client.get('/moderating')
    assert response.status_code == 200

def test_api(client: FlaskClient):
    try:
        client.post('/signup', data=dict(
            name='testuser4',
            email='test4@example.com',
            password='testpassword4',
            role_id=2
        ), follow_redirects=True)
    except:
        pass
    client.post('/login', data={'email': 'test4@example.com', 'password': 'testpassword4'})
    response = client.get('/api/get_products')
    assert response.status_code == 200

def test_booking(client: FlaskClient):
    try:
        client.post('/signup', data=dict(
            name='testuser4',
            email='test4@example.com',
            password='testpassword4',
            role_id=2
        ), follow_redirects=True)
    except:
        pass
    client.post('/login', data={'email': 'test4@example.com', 'password': 'testpassword4'})
    response = client.get('/booking')
    assert response.status_code == 200

def test_catalog(client: FlaskClient):
    try:
        client.post('/signup', data=dict(
            name='testuser4',
            email='test4@example.com',
            password='testpassword4',
            role_id=2
        ), follow_redirects=True)
    except:
        pass
    client.post('/login', data={'email': 'test4@example.com', 'password': 'testpassword4'})
    response = client.get('/catalog')
    assert response.status_code == 200

def test_list(client: FlaskClient):
    try:
        client.post('/signup', data=dict(
            name='testuser4',
            email='test4@example.com',
            password='testpassword4x',
            role_id=2
        ), follow_redirects=True)
    except:
        pass
    client.post('/login', data={'email': 'test4@example.com', 'password': 'testpassword4'})
    response = client.get('/list_reserv')
    assert response.status_code == 200

def test_delete_user_functionality(client: FlaskClient):
    try:
        response_signup = client.post('/signup', data=dict(
            name='testuser',
            email='test@example.com',
            password='testpassword',
            role_id=1
        ), follow_redirects=True)

        assert response_signup.status_code == 200

    except:
        pass

    with app.app_context():  # Добавьте контекст приложения
        user = User.query.filter_by(email='test@example.com').first()
        user_admin = User.query.filter_by(email='test4@example.com').first()

        if user:
            user_id = user.id
            user_moderate_id = user_admin.id
            response_delete = client.post(f'/delete_user/{user_id}', follow_redirects=True)
            response_delete = client.post(f'/delete_user/{user_moderate_id}', follow_redirects=True)

            assert response_delete.status_code == 200
        else:
            # Обработайте ситуацию, если пользователя не существует
            pass

