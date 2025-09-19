# Notes API

FastAPI-based REST API with authentication, role-based access control, and AWS Aurora integration.

## Features

- **User Authentication**: Register, login (JWT), protected routes
- **Notes Management**: CRUD operations for notes
- **Role-Based Access Control**: Admins can access all notes, users only their own
- **AWS Aurora Integration**: Read/write endpoint separation across AZs
- **ECS Deployment**: Load balanced with two containers for high availability

## Tech Stack

- **Backend**: FastAPI
- **Database**: AWS Aurora PostgreSQL (multi-AZ)
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **Deployment**: Docker, AWS ECS with ALB
- **CI/CD**: GitHub Actions with OIDC

## Quick Start

### Local Development

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Environment variables
export POSTGRES_SERVER=localhost
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_DB=notes_db
export SECRET_KEY=your-secret-key

# Run migrations and start
alembic upgrade head
python run.py
```

### Docker Deployment

```bash
# With Docker Compose
docker compose up --build

# Standalone with Aurora
docker run -p 8000:8000 \
  -e USE_AURORA=true \
  -e AURORA_WRITER_ENDPOINT=cluster.cluster-abc123.region.rds.amazonaws.com \
  -e AURORA_READER_ENDPOINT=cluster.cluster-ro-abc123.region.rds.amazonaws.com \
  -e AURORA_PORT=5432 \
  -e AURORA_USER=postgres \For comprehensive deployment documentation, see:
  -e AURORA_PASSWORD=secure-password \
  -e AURORA_DB=notes_db \
  -e SECRET_KEY=your-secret-key \
  notes-backend
```

## AWS Infrastructure

### Aurora Configuration
- **Writer Instance**: Primary endpoint for write operations (one AZ)
- **Reader Instance**: Read replica endpoint for read operations (different AZ)
- **Benefits**: Load distribution, high availability, disaster recovery
- **Connection Management**: Application routes queries to appropriate endpoint

### ECS Deployment
- **Load Balancer**: Application Load Balancer routing traffic to containers
- **Containers**: Two application containers running in different AZs
- **Auto Scaling**: Configured to maintain high availability
- **Health Checks**: ALB monitors container health

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Get JWT token
- `GET /api/v1/auth/me` - Get current user

### Notes
- `GET /api/v1/notes/` - List notes
- `POST /api/v1/notes/` - Create note
- `GET /api/v1/notes/{note_id}` - Get note
- `PUT /api/v1/notes/{note_id}` - Update note
- `DELETE /api/v1/notes/{note_id}` - Delete note
- `GET /api/v1/notes/by-user/{user_id}` - Get user notes (admin only)

## Project Structure

```
├── alembic/            # Database migrations
├── app/                # Application code
│   ├── api/            # API endpoints
│   ├── core/           # Config and dependencies
│   ├── db/             # Database session
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   └── utils/          # Utilities
├── tests/              # Tests
└── scripts/            # Helper scripts
```

## Testing

```bash
# Run tests
pytest

# With coverage
./run_tests.sh
```

## CI/CD Pipeline

- **Trigger**: Push to main branch or manual workflow run
- **Process**: Build → Test → Push to ECR → Deploy to ECS
- **Security**: OIDC for AWS authentication
- **Deployment Strategy**: Rolling deployment to minimize downtime
- **Monitoring**: CloudWatch Logs, ECS service events, ALB metrics