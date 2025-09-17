# Notes Application API

A FastAPI-based REST API for a notes application with user authentication and role-based access control.

## Features

- User Authentication
  - Sign-up (name, email, password, role: admin or user)
  - Sign-in (with JWT token)
  - Protected routes for logged-in users

- Notes Management
  - Create new notes (title + description)
  - View all notes
  - Edit existing notes
  - Delete notes

- Role-Based Access Control
  - Admin users can view, edit, and delete any note
  - Regular users can only manage their own notes

## Tech Stack

- Backend: Python (FastAPI)
- Database: PostgreSQL
- ORM: SQLAlchemy
- Authentication: JWT
- Testing: pytest

## Project Structure

```
.
├── alembic/            # Database migrations
├── app/                # Application code
│   ├── api/            # API endpoints
│   │   └── endpoints/  # API route handlers
│   ├── core/           # Core components and config
│   ├── db/             # Database related code
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   └── utils/          # Utility functions
├── tests/              # Test cases
└── alembic.ini         # Alembic configuration
```

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- Docker (for containerization)
- AWS CLI (for deployment)

### Installation

1. Clone the repository

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
export POSTGRES_SERVER=localhost
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_DB=notes_db
export SECRET_KEY=your-secret-key-for-jwt
```

5. Create the database:

```bash
createdb notes_db
```

6. Run migrations:

```bash
alembic upgrade head
```

### Running the Application

```bash
python run.py
```

Or using uvicorn directly:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation (Swagger UI) will be available at `http://localhost:8000/docs`

### Running Tests

```bash
pytest
```

### Containerization

Build the Docker image:

```bash
docker build -t notes-backend .
```

Run the container:

```bash
docker run -p 8000:8000 -e DATABASE_URL=postgres://user:pass@host/db -e SECRET_KEY=mysecretkey notes-backend
```

### CI/CD Pipeline

This project uses GitHub Actions for CI/CD:

1. When code is pushed to the main branch, the pipeline:
   - Builds the application
   - Runs tests
   - Builds a Docker image
   - Pushes the image to AWS ECR
   - Deploys to AWS EKS

2. Required AWS secrets in GitHub:
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY

3. The pipeline status can be checked in the GitHub Actions tab.

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login to get JWT token
- `GET /api/v1/auth/me` - Get current user info

### Notes

- `GET /api/v1/notes/` - Get all notes (filtered by user role)
- `POST /api/v1/notes/` - Create a new note
- `GET /api/v1/notes/{note_id}` - Get a specific note
- `PUT /api/v1/notes/{note_id}` - Update a note
- `DELETE /api/v1/notes/{note_id}` - Delete a note