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

The application uses GitHub Actions with OIDC authentication for secure continuous integration and deployment to AWS.

### GitHub Actions Workflow

The CI/CD pipeline is configured in `.github/workflows/ci-cd.yml` and performs the following steps:

1. Checkout code repository
2. Configure AWS credentials using OIDC
3. Log in to Amazon ECR
4. Build and push Docker image
5. Update ECS task definition
6. Deploy to Amazon ECS
7. Verify deployment status

### Docker Entrypoint

The application uses a custom Docker entrypoint script that:

1. Waits for the database to be available
2. Runs database migrations
3. Starts the FastAPI application

### Deployment Documentation

We have comprehensive documentation for the deployment process:

- [CI/CD Overview](./docs/cicd_overview.md) - Overview of the CI/CD pipeline
- [Deployment Summary](./docs/deployment_summary.md) - Summary of the entire deployment setup
- [Deployment Checklist](./docs/deployment_checklist.md) - Checklist for production deployments
- [ECS Monitoring](./docs/ecs_monitoring.md) - Guide to monitor ECS deployments
- [Developer Guide](./docs/developer_guide.md) - Quick start guide for new developers
- [OIDC Setup Guide](./.github/workflows/setup-guide.md) - Setup instructions for AWS OIDC

### Security and Authentication

The CI/CD pipeline uses OpenID Connect (OIDC) for secure authentication between GitHub Actions and AWS, eliminating the need for storing long-lived credentials in GitHub.

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

### Docker Deployment

#### Running with Docker Compose

The application can be run using Docker Compose, which sets up the application with the correct environment variables:

1. Make sure your `.env` file is properly configured with either PostgreSQL or Aurora connection details.

2. Build and start the containers:

```bash
docker compose up --build
```

Or use the provided helper script:

```bash
./scripts/docker_run.sh --build --logs
```

The API will be available at `http://localhost:8000`

#### Running with Docker (standalone)

1. Build the Docker image:

```bash
docker build -t notes-backend .
```

2. Run the container with appropriate environment variables:

```bash
# For AWS Aurora
docker run -p 8000:8000 \
  -e USE_AURORA=true \
  -e AURORA_WRITER_ENDPOINT=your-cluster-name.cluster-abcdefghijkl.region.rds.amazonaws.com \
  -e AURORA_READER_ENDPOINT=your-cluster-name.cluster-ro-abcdefghijkl.region.rds.amazonaws.com \
  -e AURORA_PORT=5432 \
  -e AURORA_USER=postgres \
  -e AURORA_PASSWORD=your-secure-password \
  -e AURORA_DB=notes_db \
  -e SECRET_KEY=your-secret-key \
  notes-backend
```

For detailed Docker setup instructions, see [Docker Setup Documentation](./docs/docker_setup.md).

### Deployment Process

The application is deployed to AWS ECS using a CI/CD pipeline with GitHub Actions:

1. **Automatic Deployment**: When code is pushed to the main branch, the pipeline automatically builds and deploys the application.

2. **Manual Deployment**: You can manually trigger a deployment from the GitHub Actions tab:
   - Navigate to Actions > Build, Push, and Deploy workflow
   - Click "Run workflow"
   - Select branch and click "Run workflow"

3. **Monitoring Deployments**: 
   - Check GitHub Actions workflow status
   - Monitor ECS service events in AWS Console
   - View CloudWatch logs for application logs

For comprehensive deployment documentation, see:

- [Deployment Summary](./docs/deployment_summary.md) - Overview of the deployment setup
- [CI/CD Overview](./docs/cicd_overview.md) - Details of the CI/CD pipeline
- [ECS Monitoring Guide](./docs/ecs_monitoring.md) - How to monitor and troubleshoot deployments

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