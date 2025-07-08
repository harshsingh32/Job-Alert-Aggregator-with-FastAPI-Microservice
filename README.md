# Job Alert Aggregator

A comprehensive job alert system built with Django (backend), FastAPI (scraper microservice), and modern web technologies.

## 🚀 Features

- **User Management**: Registration, authentication, and profile management
- **Job Preferences**: Set keywords, location, salary range, and job type preferences
- **Multi-source Scraping**: Scrape jobs from RemoteOK, Indeed, LinkedIn, and more
- **Intelligent Matching**: Smart job matching based on user preferences
- **Real-time Alerts**: Email notifications for new job matches
- **Admin Dashboard**: Monitor scraping logs and system health
- **Scalable Architecture**: Microservices with Docker containerization

## 🛠️ Tech Stack

### Backend (Django)
- **Framework**: Django 4.2 with Django REST Framework
- **Authentication**: JWT tokens with refresh capability
- **Database**: PostgreSQL with optimized queries
- **Task Queue**: Celery with Redis for background jobs
- **Email**: SMTP integration for job alerts

### Scraper Service (FastAPI)
- **Framework**: FastAPI for high-performance API
- **Async Processing**: Asynchronous job scraping
- **Multiple Sources**: RemoteOK, Indeed, LinkedIn scrapers
- **Rate Limiting**: Respectful scraping with delays

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx for load balancing
- **Monitoring**: Comprehensive logging and health checks
- **CI/CD**: GitHub Actions for automated deployment

## 📁 Project Structure

```
job-alert-aggregator/
├── backend/                 # Django backend service
│   ├── jobaggregator/      # Django project configuration
│   ├── users/              # User management app
│   ├── jobs/               # Job and matching logic
│   └── requirements.txt    # Python dependencies
├── scraper/                # FastAPI scraper service
│   ├── app/
│   │   ├── services/       # Scraping logic
│   │   └── api/           # API endpoints
│   └── requirements.txt
├── nginx/                  # Nginx configuration
├── docker-compose.yml      # Service orchestration
└── .env                   # Environment variables
```

## 🚦 Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+
- Redis 7+

### Quick Start with Docker

1. **Clone the repository**
```bash
git clone <repository-url>
cd job-alert-aggregator
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Run migrations**
```bash
docker-compose exec backend python manage.py migrate
```

5. **Create superuser**
```bash
docker-compose exec backend python manage.py createsuperuser
```

6. **Access the application**
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin
- Scraper API: http://localhost:8001
- API Documentation: http://localhost:8001/docs

### Local Development

1. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

2. **Scraper Service**
```bash
cd scraper
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

3. **Background Tasks**
```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Celery worker
cd backend
celery -A jobaggregator worker --loglevel=info

# Terminal 3: Start Celery beat
cd backend
celery -A jobaggregator beat --loglevel=info
```

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/token/refresh/` - Token refresh

### User Management
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile
- `GET /api/auth/preferences/` - Get job preferences
- `POST /api/auth/preferences/` - Create job preference

### Jobs
- `GET /api/jobs/` - List jobs with filtering
- `GET /api/jobs/{id}/` - Get job details
- `GET /api/jobs/matches/` - Get user's job matches
- `POST /api/jobs/{id}/bookmark/` - Bookmark job
- `POST /api/jobs/{id}/apply/` - Mark job as applied

### Scraper Service
- `GET /scraper/` - Service health check
- `GET /scraper/scrapers` - Available scrapers
- `POST /scraper/scrape/{scraper_name}` - Scrape specific source
- `POST /scraper/scrape/batch` - Batch scrape all sources

## 🔧 Configuration

### Environment Variables

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:password@db:5432/jobdb
ALLOWED_HOSTS=localhost,127.0.0.1

# Redis & Celery
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Services
SCRAPER_SERVICE_URL=http://scraper:8001
```

### Job Board Configuration

Add new job boards through the Django admin interface:

```python
{
    "name": "RemoteOK",
    "base_url": "https://remoteok.io",
    "scraper_config": {
        "api_endpoint": "/api",
        "rate_limit": 1
    }
}
```

## 🔍 Monitoring & Logging

### Health Checks
- Backend: `GET /api/health/`
- Scraper: `GET /scraper/health`

### Logs
- Application logs: `logs/django.log`
- Celery logs: Console output
- Scraper logs: FastAPI console

### Admin Dashboard
Access comprehensive monitoring at `/admin`:
- User management
- Job preferences
- Scrape logs
- Email notifications
- System health

## 🚀 Deployment

### Production Deployment

1. **Update environment variables**
```bash
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.com
```

2. **Use production database**
```bash
DATABASE_URL=postgres://user:password@your-db-host:5432/jobdb
```

3. **Set up SSL with Let's Encrypt**
```bash
# Add to docker-compose.yml
certbot:
  image: certbot/certbot
  volumes:
    - ./certbot/conf:/etc/letsencrypt
    - ./certbot/www:/var/www/certbot
```

4. **Configure email properly**
```bash
EMAIL_HOST=your-smtp-server
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-app-password
```

### CI/CD Pipeline

The project includes GitHub Actions workflow for:
- Automated testing
- Docker image building
- Deployment to staging/production
- Health checks

## 📈 Performance Optimization

### Database
- Indexed fields for faster queries
- Connection pooling
- Query optimization

### Caching
- Redis for session and task caching
- Database query caching
- Static file caching with Nginx

### Scaling
- Horizontal scaling with Docker Swarm
- Load balancing with Nginx
- Background task distribution

## 🔐 Security

### Authentication
- JWT tokens with refresh capability
- Password hashing with Django's built-in security
- Rate limiting on API endpoints

### Data Protection
- SQL injection prevention
- XSS protection
- CSRF protection
- Secure headers

### Privacy
- Data encryption at rest
- Secure API communication
- User data anonymization options

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 💬 Support

For support, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information
4. Contact the development team

## 🎯 Roadmap

- [ ] Machine learning job matching
- [ ] Mobile app development
- [ ] Additional job board integrations
- [ ] Advanced analytics dashboard
- [ ] Social features (job sharing, reviews)
- [ ] API rate limiting improvements
- [ ] Multi-language support