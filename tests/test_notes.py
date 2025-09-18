import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.note import Note
from tests.utils import create_test_user, create_test_note


def get_auth_header(client, user_email="test@example.com", user_password="password123"):
    """Helper function to get authentication headers"""
    login_data = {
        "username": user_email,  # OAuth2 form expects 'username', not 'email'
        "password": user_password
    }
    login_response = client.post("/api/v1/auth/login", data=login_data)
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_note(client: TestClient, db: Session):
    """
    Test creating a note
    """
    # Create a test user
    user = create_test_user(db)
    auth_header = get_auth_header(client)
    
    # Create a note
    note_data = {
        "title": "Test Note",
        "description": "This is a test note"
    }
    
    response = client.post(
        "/api/v1/notes/",
        json=note_data,
        headers=auth_header
    )
    assert response.status_code == 201
    
    data = response.json()
    assert data["title"] == note_data["title"]
    assert data["description"] == note_data["description"]
    assert data["owner_id"] == user.id
    assert "id" in data
    
    # Check that the note was actually created in the database
    note = db.query(Note).filter(Note.id == data["id"]).first()
    assert note is not None
    assert note.title == note_data["title"]
    assert note.description == note_data["description"]
    assert note.owner_id == user.id


def test_get_user_notes(client: TestClient, db: Session):
    """
    Test getting all notes for a user
    """
    # Create a test user
    user = create_test_user(db)
    auth_header = get_auth_header(client)
    
    # Create some test notes
    create_test_note(db, user.id, "Note 1", "Description 1")
    create_test_note(db, user.id, "Note 2", "Description 2")
    
    # Get all notes
    response = client.get("/api/v1/notes/", headers=auth_header)
    assert response.status_code == 200
    
    data = response.json()
    # Check for paginated response structure
    assert "items" in data
    assert "meta" in data
    assert data["meta"]["total"] == 2
    
    # Check the notes data in items array
    notes = data["items"]
    assert len(notes) == 2
    
    # The notes may be in reverse order due to sorting by created_at desc
    note_titles = [note["title"] for note in notes]
    assert "Note 1" in note_titles
    assert "Note 2" in note_titles
    
    # Check descriptions
    for note in notes:
        if note["title"] == "Note 1":
            assert note["description"] == "Description 1"
        elif note["title"] == "Note 2":
            assert note["description"] == "Description 2"


def test_get_note_by_id(client: TestClient, db: Session):
    """
    Test getting a note by ID
    """
    # Create a test user
    user = create_test_user(db)
    auth_header = get_auth_header(client)
    
    # Create a test note
    note = create_test_note(db, user.id)
    
    # Get the note by ID
    response = client.get(f"/api/v1/notes/{note.id}", headers=auth_header)
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == note.id
    assert data["title"] == note.title
    assert data["description"] == note.description
    assert data["owner_id"] == note.owner_id


def test_get_nonexistent_note(client: TestClient, db: Session):
    """
    Test getting a note that doesn't exist
    """
    # Create a test user
    user = create_test_user(db)
    auth_header = get_auth_header(client)
    
    # Try to get a note that doesn't exist
    response = client.get("/api/v1/notes/999", headers=auth_header)
    assert response.status_code == 404


def test_update_note(client: TestClient, db: Session):
    """
    Test updating a note
    """
    # Create a test user
    user = create_test_user(db)
    auth_header = get_auth_header(client)
    
    # Create a test note
    note = create_test_note(db, user.id)
    
    # Update the note
    update_data = {
        "title": "Updated Title",
        "description": "Updated description"
    }
    
    response = client.put(
        f"/api/v1/notes/{note.id}",
        json=update_data,
        headers=auth_header
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == note.id
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]
    
    # Check that the note was actually updated in the database
    updated_note = db.query(Note).filter(Note.id == note.id).first()
    assert updated_note.title == update_data["title"]
    assert updated_note.description == update_data["description"]


def test_delete_note(client: TestClient, db: Session):
    """
    Test deleting a note
    """
    # Create a test user
    user = create_test_user(db)
    auth_header = get_auth_header(client)
    
    # Create a test note
    note = create_test_note(db, user.id)
    
    # Delete the note
    response = client.delete(f"/api/v1/notes/{note.id}", headers=auth_header)
    assert response.status_code == 200
    
    # Check that the note was actually deleted from the database
    deleted_note = db.query(Note).filter(Note.id == note.id).first()
    assert deleted_note is None