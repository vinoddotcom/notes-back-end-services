import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import User, UserRole
from tests.utils import create_test_user


@pytest.fixture(scope="function")
def clean_tables(db: Session):
    """Clear all tables before tests"""
    # First clear all data
    db.query(User).delete()
    db.commit()
    yield


@pytest.mark.usefixtures("clean_tables")
def test_list_users_as_admin(client: TestClient, db: Session):
    """Test getting list of users as admin"""
    # Create an admin user
    admin_user = create_test_user(db, email="admin@example.com", role=UserRole.ADMIN)
    admin_token = create_user_token(client, admin_user.email)
    
    # Create some regular users
    create_test_user(db, email="user1@example.com")
    create_test_user(db, email="user2@example.com")
    
    # Test listing all users as admin
    response = client.get(
        "/api/v1/admin/users/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "meta" in data
    assert len(data["items"]) >= 3  # Admin + at least 2 other users
    
    # Verify expected fields in response
    user_emails = [user["email"] for user in data["items"]]
    assert "admin@example.com" in user_emails
    assert "user1@example.com" in user_emails
    assert "user2@example.com" in user_emails


@pytest.mark.usefixtures("clean_tables")
def test_list_users_as_non_admin(client: TestClient, db: Session):
    """Test that regular users cannot access admin routes"""
    # Create a regular user
    user = create_test_user(db, email="user@example.com")
    token = create_user_token(client, user.email)
    
    # Try to list all users
    response = client.get(
        "/api/v1/admin/users/",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 403  # Forbidden


@pytest.mark.usefixtures("clean_tables")
def test_get_user_details_as_admin(client: TestClient, db: Session):
    """Test getting specific user details as admin"""
    # Create an admin user
    admin_user = create_test_user(db, email="admin@example.com", role=UserRole.ADMIN)
    admin_token = create_user_token(client, admin_user.email)
    
    # Create a regular user
    user = create_test_user(db, email="user@example.com")
    
    # Test getting user details as admin
    response = client.get(
        f"/api/v1/admin/users/{user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"
    assert "notes" in data  # Should include notes field


@pytest.mark.usefixtures("clean_tables")
def test_update_user_role_as_admin(client: TestClient, db: Session):
    """Test updating user role as admin"""
    # Create an admin user
    admin_user = create_test_user(db, email="admin@example.com", role=UserRole.ADMIN)
    admin_token = create_user_token(client, admin_user.email)
    
    # Create a regular user
    user = create_test_user(db, email="user@example.com")
    
    # Update user role to admin
    response = client.put(
        f"/api/v1/admin/users/{user.id}/role",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"role": "admin"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"
    
    # Verify change in database
    updated_user = db.query(User).filter(User.id == user.id).first()
    assert updated_user.role == UserRole.ADMIN


@pytest.mark.usefixtures("clean_tables")
def test_update_user_status_as_admin(client: TestClient, db: Session):
    """Test activating/deactivating a user as admin"""
    # Create an admin user
    admin_user = create_test_user(db, email="admin@example.com", role=UserRole.ADMIN)
    admin_token = create_user_token(client, admin_user.email)
    
    # Create a regular user
    user = create_test_user(db, email="user@example.com")
    
    # Deactivate the user
    response = client.put(
        f"/api/v1/admin/users/{user.id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": False}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] == False
    
    # Verify change in database
    updated_user = db.query(User).filter(User.id == user.id).first()
    assert updated_user.is_active == False


@pytest.mark.usefixtures("clean_tables")
def test_admin_cannot_deactivate_self(client: TestClient, db: Session):
    """Test that admin cannot deactivate themselves"""
    # Create an admin user
    admin_user = create_test_user(db, email="admin@example.com", role=UserRole.ADMIN)
    admin_token = create_user_token(client, admin_user.email)
    
    # Try to deactivate self
    response = client.put(
        f"/api/v1/admin/users/{admin_user.id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": False}
    )
    
    assert response.status_code == 400  # Bad request
    assert "cannot deactivate themselves" in response.json()["detail"]


# Helper function to create token for a user
def create_user_token(client: TestClient, email: str) -> str:
    """Helper to create a user token for testing"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "password123"},
    )
    return response.json()["access_token"]