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

## CI/CD Pipeline

The application uses GitHub Actions for continuous integration and deployment to AWS.

### GitHub Actions Workflow

The CI/CD pipeline is configured in `.github/workflows/backend-deploy.yml` and performs the following steps:

1. Run tests
2. Build a Docker image
3. Push the image to Amazon ECR
4. Deploy to Amazon ECS
5. Run database migrations

### SSM Parameter Integration

The workflow uses AWS SSM Parameter Store to retrieve information about deployed resources:

- ECR repository URL
- ECS cluster name
- ECS service name
- Task execution role ARN
- Database secret ARN
- VPC subnet IDs

### Setting Up GitHub Secrets

The following secrets need to be configured in your GitHub repository:

1. `AWS_ACCESS_KEY_ID`: IAM user's access key ID
2. `AWS_SECRET_ACCESS_KEY`: IAM user's secret access key
3. `AWS_REGION`: AWS region (e.g., ap-south-1)

Use the provided script to get IAM credentials:

```bash
./scripts/get_github_credentials.sh
```

### Deployment Validation

To validate that all required SSM parameters are set up correctly:

```bash
./scripts/validate_ssm_params.sh
```

For more information on the CI/CD setup, see the [CI/CD Setup Documentation](./docs/cicd_setup.md).

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
   - Runs tests
   - Builds a Docker image
   - Pushes the image to AWS ECR
   - Deploys to AWS ECS
   - Runs database migrations

2. Authentication with AWS (two options):
   
   **Option 1: IAM User with Access Keys**
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - AWS_REGION
   
   **Option 2: OIDC Authentication (Recommended)**
   - AWS_ROLE_ARN
   - AWS_REGION

3. The pipeline status can be checked in the GitHub Actions tab.

For detailed deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md).
For OIDC setup instructions, see [OIDC Setup Guide](./docs/oidc_setup.md).

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