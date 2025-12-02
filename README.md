# Pour Your Mind - Backend API

A Django REST API for sharing thoughts publicly with optional anonymity and reply functionality.

## Features

- Share thoughts publicly
- Post anonymously or with your name
- Reply to others' thoughts
- View all thoughts in a paginated feed
- RESTful API endpoints

## API Endpoints

- `GET /api/notes/` - Get all notes with pagination
- `GET /api/notes/{id}/` - Get note detail with replies
- `POST /api/notes/submit/` - Submit new note
- `POST /api/notes/{id}/reply/` - Submit reply to note
- `GET /api/about/` - Get about information

## Deployment Options

### Option 1: Docker Compose

#### Development

1. **Build and run with development settings:**

```bash
docker-compose -f docker-compose.dev.yml up --build
```

2. **Run migrations:**

```bash
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate
```

3. **Create superuser:**

```bash
docker-compose -f docker-compose.dev.yml exec web python manage.py createsuperuser
```

4. **Access the application:**
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/

#### Production

1. **Build and run with production settings:**

```bash
docker-compose up --build
```

2. **Run migrations:**

```bash
docker-compose exec web python manage.py migrate
```

3. **Create superuser:**

```bash
docker-compose exec web python manage.py createsuperuser
```

4. **Access the application:**
   - API: http://localhost/api/
   - Admin: http://localhost/admin/

### Option 2: Kubernetes

#### Prerequisites

- Kubernetes cluster
- kubectl configured
- Docker image built and pushed to registry

#### Quick Deploy

1. **Build and push Docker image:**

```bash
docker build -t your-registry.com/pour-your-mind:latest .
docker push your-registry.com/pour-your-mind:latest
```

2. **Update image reference in `k8s/django-deployment.yaml`**

3. **Deploy to Kubernetes:**

```bash
cd k8s
./deploy.sh
```

4. **Access the application:**

```bash
kubectl port-forward -n pour-your-mind service/nginx-service 8080:80
# Open http://localhost:8080
```

For detailed Kubernetes deployment instructions, see [k8s/README.md](k8s/README.md).

## Local Development (without Docker)

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

2. **Run migrations:**

```bash
python manage.py migrate
```

3. **Create superuser:**

```bash
python manage.py createsuperuser
```

4. **Run development server:**

```bash
python manage.py runserver
```

## Project Structure

```
pym_be/
├── notes/                    # Main Django app
│   ├── applications/         # Business logic
│   │   ├── model_methods.py # Model methods and properties
│   │   └── note_validators.py # Validation logic
│   ├── models.py            # Database models
│   ├── views.py             # API views
│   ├── urls.py              # URL routing
│   ├── forms.py             # Django forms
│   ├── admin.py             # Admin interface
│   └── schema.py            # Pydantic schemas
├── pym_be/                  # Django project settings
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Production Docker setup
├── docker-compose.dev.yml  # Development Docker setup
└── nginx.conf              # Nginx configuration
```

## Environment Variables

- `DEBUG` - Django debug mode (0 for production, 1 for development)
- `DATABASE_URL` - Database connection string
- `POSTGRES_DB` - PostgreSQL database name
- `POSTGRES_USER` - PostgreSQL username
- `POSTGRES_PASSWORD` - PostgreSQL password
- `DB_HOST` - Database host
- `DB_PORT` - Database port

## API Usage Examples

### Get all notes

```bash
curl http://localhost:8000/api/notes/
```

### Submit a new note

```bash
curl -X POST http://localhost:8000/api/notes/submit/ \
  -H "Content-Type: application/json" \
  -d '{"content": "This is my thought!", "author_name": "John"}'
```

### Reply to a note

```bash
curl -X POST http://localhost:8000/api/notes/1/reply/ \
  -H "Content-Type: application/json" \
  -d '{"content": "Great thought!", "author_name": "Jane"}'
```
