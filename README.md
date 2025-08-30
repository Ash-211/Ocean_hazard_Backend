# Ocean Hazard Reporting System

A comprehensive platform for reporting and monitoring ocean hazards, built with FastAPI, PostgreSQL with PostGIS, and Celery for background processing.

## Features

### Core Functionality
- ✅ Hazard reporting with geospatial data (latitude/longitude)
- ✅ GeoJSON API endpoints for map visualization
- ✅ Real-time hazard monitoring
- ✅ Bounding box filtering for regional data

### Newly Added Features
- 🔐 **JWT Authentication** - User registration, login, and role-based access
- 👥 **User Management** - Citizen, official, and analyst roles
- 📱 **Media Upload Support** - Image, video, and audio attachments
- 🤖 **Celery Background Tasks** - Asynchronous processing
- 📊 **Social Media Integration** - Twitter and news scraping
- 🧠 **NLP Processing** - Hazard detection and sentiment analysis
- 🔥 **Hotspot Generation** - Dynamic hazard clustering
- 📈 **Trend Analysis** - Real-time hazard trend detection

## Architecture

```
Frontend (Mobile/Web)
    │
    ▼
FastAPI Backend (REST API)
    │
    ├── Authentication (JWT)
    ├── Hazard Reporting
    ├── Media Upload
    ├── GeoJSON API
    │
    ▼
PostgreSQL + PostGIS
    │
    ├── Users & Roles
    ├── Hazard Reports
    ├── Media Files
    │
    ▼
Celery Workers
    │
    ├── Social Media Scraping
    ├── NLP Processing
    ├── Hotspot Generation
    └── Trend Analysis
```

## Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.8+
- Redis (for Celery)

### Installation

1. **Clone and setup:**
```bash
git clone <repository>
cd ocean_hazard_backend
```

2. **Environment variables:**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Start with Docker:**
```bash
docker-compose up -d
```

4. **Or run locally:**
```bash
# Install dependencies
pip install -r requirements.txt

# Start Redis
redis-server

# Start Celery worker
celery -A celery_app worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A celery_app beat --loglevel=info

# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/token` - Login (get JWT token)
- `POST /auth/logout` - Logout
- `GET /auth/me` - Get current user info
- `GET /auth/users` - List users (admin only)

### Hazard Reports
- `POST /hazards/` - Create new hazard report (authenticated)
- `GET /hazards/geojson` - Get hazards as GeoJSON
- `GET /hazards/geojson?bbox=minLon,minLat,maxLon,maxLat` - Filter by bounding box

### Social Media & Analysis
- `POST /tasks/scrape-twitter` - Trigger Twitter scraping
- `GET /tasks/hotspots` - Get current hazard hotspots
- `POST /tasks/analyze-text` - NLP analysis endpoint

## Database Schema

### Tables
- `users` - User accounts and roles
- `hazard_reports` - Hazard reports with geometry
- `media` - Uploaded media files
- `user_sessions` - JWT token sessions

### User Roles
- `citizen` - Basic reporting access
- `official` - View all reports, moderate content
- `analyst` - Full access, can manage users

## Background Tasks

### Celery Tasks
1. **Social Media Monitoring** - Scrape Twitter and news sites
2. **NLP Processing** - Analyze text for hazard detection
3. **Hotspot Generation** - Cluster reports by location
4. **Trend Analysis** - Detect emerging hazard patterns

### Scheduled Tasks
- Hourly social media scraping
- Real-time hotspot updates
- Daily trend reports

## Configuration

### Environment Variables
```env
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-jwt-secret-key
CELERY_BROKER_URL=redis://localhost:6379/0
TWITTER_BEARER_TOKEN=your-twitter-token
```

### File Upload
- Max file size: 10MB
- Allowed types: images, videos, audio
- Storage: Local filesystem or cloud storage

## Development

### Testing
```bash
# Run comprehensive tests
python test_comprehensive.py

# Test authentication
python test_auth.py

# Test API endpoints
python test_api.py
```

### Adding New Features

1. **New Models**: Add to `models.py`
2. **API Routes**: Create new router in appropriate module
3. **Background Tasks**: Add to `tasks/` directory
4. **Authentication**: Use `@router.post("/endpoint")` with auth dependencies

## Deployment

### Production Checklist
- [ ] Change JWT secret key
- [ ] Set proper CORS origins
- [ ] Configure database connection pooling
- [ ] Set up file storage (S3/Cloud Storage)
- [ ] Configure SSL certificates
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

### Cloud Deployment
The application is containerized and can be deployed to:
- AWS ECS/EKS
- Google Cloud Run
- Azure Container Apps
- Heroku with Redis addon

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Email: support@incois.gov.in
- Documentation: [INCOIS Website](https://incois.gov.in)

## Acknowledgments

- Indian National Centre for Ocean Information Services (INCOIS)
- Ministry of Earth Sciences, Government of India
- FastAPI and PostgreSQL communities
