# Django Skeleton

A modern Django project skeleton with `uv` package manager and Docker Compose setup.

## Features

- 🐍 **Python 3.13** with `uv` package manager
- 🐳 **Docker & Docker Compose** for easy development and deployment
- 🗄️ **Auto-database detection**: SQLite for `uv`, PostgreSQL for Docker
- 🔐 **JWT Authentication** with refresh tokens
- 👤 **Custom User Model** with email-based login
- 📦 **WhiteNoise** for static file serving
- 🔧 **Environment variables** with `python-decouple`
- 🚀 **Gunicorn** for production WSGI server
- 🎨 **Ruff** for code formatting and linting
- 🔒 **Security best practices** configured

## Quick Start

### Prerequisites

- Python 3.13+
- Docker and Docker Compose
- `uv` package manager

### Quick Start

```bash
git clone <your-repo>
cd django-skeleton

# For local development with uv (SQLite)
./scripts/dev.sh uv

# For Docker development (PostgreSQL)
./scripts/dev.sh docker
```

### Development Setup

#### Option 1: Local Development with uv (SQLite)

**Automatic setup:**
```bash
./scripts/dev.sh uv
```

**Manual setup:**
1. **Clone and setup environment:**
   ```bash
   git clone <your-repo>
   cd django-skeleton
   cp .env.example .env
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Run migrations:**
   ```bash
   uv run python manage.py migrate
   ```

4. **Create superuser:**
   ```bash
   uv run python manage.py createsuperuser
   ```

5. **Start development server:**
   ```bash
   uv run python manage.py runserver
   ```

6. **Access the application:**
   - Django app: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

#### Option 2: Docker Development (PostgreSQL)

**Automatic setup:**
```bash
./scripts/dev.sh docker
```

**Manual setup:**
1. **Setup environment:**
   ```bash
   cp .env.docker .env
   ```

2. **Run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Django app: http://localhost:8000
   - Admin panel: http://localhost:8000/admin


## Production Deployment

1. **Setup environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

2. **Deploy with production compose:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## Project Structure

```
django-skeleton/
├── config/                 # Django project settings
│   ├── __init__.py
│   ├── settings.py        # Main settings file
│   ├── urls.py           # URL configuration
│   └── wsgi.py           # WSGI configuration
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
├── docker-compose.yml   # Development Docker setup
├── docker-compose.prod.yml # Production Docker setup
├── Dockerfile           # Docker image configuration
├── manage.py           # Django management script
├── pyproject.toml      # Project dependencies and config
├── README.md           # This file
└── uv.lock            # Locked dependencies
```

## Available Commands

### Development
```bash
# Install dependencies
uv sync

# Run development server
uv run python manage.py runserver

# Run migrations
uv run python manage.py migrate

# Create superuser
uv run python manage.py createsuperuser

# Collect static files
uv run python manage.py collectstatic

# Run tests
uv run python manage.py test
```

### Code Quality

#### Pre-commit Setup

This project uses pre-commit hooks to ensure code quality. Setup pre-commit hooks:

```bash
# Install pre-commit (already included in dev dependencies)
uv sync

# Install git hooks
uv run pre-commit install

# Run pre-commit on all files (optional)
uv run pre-commit run --all-files
```

Pre-commit hooks will automatically run on every commit and include:
- **Ruff check**: Lint Python code and fix issues
- **Ruff format**: Format Python code
- **uv sync**: Ensure dependencies are up to date

#### Manual Code Quality Commands
```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Fix linting issues
uv run ruff check --fix .

# Run pre-commit manually
uv run pre-commit run --all-files
```

### Docker
```bash
# Development
docker-compose up --build
docker-compose down

# Production
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml down
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Settings
DB_NAME=django_skeleton
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Static Files
STATIC_URL=/static/
STATIC_ROOT=/app/staticfiles/

# Media Files
MEDIA_URL=/media/
MEDIA_ROOT=/app/media/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Setup pre-commit hooks: `uv run pre-commit install`
4. Make your changes
5. Pre-commit hooks will run automatically on commit
6. If hooks fail, fix the issues and commit again
7. Run tests: `uv run python manage.py test`
8. Push to the branch
9. Create a Pull Request

## License

This project is licensed under the MIT License.
