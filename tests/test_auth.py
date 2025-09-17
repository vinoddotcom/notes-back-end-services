import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.utils.auth import get_password_hash
from tests.utils import create_test_user


def test_register_user(client: TestClient, db: Session):
    """
    Test user registration endpoint
    """
    user_data = {
        "email": "newuser@example.com",
        "password": "strongpassword123",
        "name": "New User",
        "role": "user"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    
    data = response.json()
    assert "id" in data
    assert data["email"] == user_data["email"]
    assert data["name"] == user_data["name"]
    assert data["role"] == user_data["role"]
    assert "password" not in data
    
    # Check that the user was actually created in the database
    user = db.query(User).filter(User.email == user_data["email"]).first()
    assert user is not None
    assert user.email == user_data["email"]
    assert user.name == user_data["name"]
    assert user.role == user_data["role"]


def test_register_user_duplicate_email(client: TestClient, db: Session):
    """
    Test registration with an email that already exists
    """
    # Create a user with the email
    create_test_user(db, email="existing@example.com")
    
    # Try to register with the same email
    user_data = {
        "email": "existing@example.com",
        "password": "strongpassword123",
        "name": "Another User",
        "role": "user"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "email already registered" in response.json()["detail"].lower()


def test_login_user(client: TestClient, db: Session):
    """
    Test user login endpoint
    """
    # Create a test user
    user = create_test_user(db)
    
    # Login with the correct credentials
    login_data = {
        "username": "test@example.com",  # OAuth2 form expects 'username', not 'email'
        "password": "password123"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_user_wrong_password(client: TestClient, db: Session):
    """
    Test login with wrong password
    """
    # Create a test user
    user = create_test_user(db)
    
    # Try to login with wrong password
    login_data = {
        "username": "test@example.com",  # OAuth2 form expects 'username', not 'email'
        "password": "wrongpassword"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401
    assert "incorrect email or password" in response.json()["detail"].lower()


def test_login_nonexistent_user(client: TestClient, db: Session):
    """
    Test login with non-existent user
    """
    login_data = {
        "username": "nonexistent@example.com",  # OAuth2 form expects 'username', not 'email'
        "password": "password123"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401
    assert "incorrect email or password" in response.json()["detail"].lower()


def test_get_current_user(client: TestClient, db: Session):
    """
    Test getting the current user's information
    """
    # Create a test user
    user = create_test_user(db)
    
    # Login to get a token
    login_data = {
        "username": "test@example.com",  # OAuth2 form expects 'username', not 'email'
        "password": "password123"
    }
    login_response = client.post("/api/v1/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    
    # Get the current user with the token
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == user.email
    assert data["name"] == user.name
    assert data["id"] == user.id