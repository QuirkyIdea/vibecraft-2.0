# Inventix AI - Docker Deployment Guide

This guide covers deploying Inventix AI using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+ ([Install Docker](https://docs.docker.com/engine/install/))
- Docker Compose V2+ (included with Docker Desktop)
- Your Gemini API Key from [Google AI Studio](https://aistudio.google.com/)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd INVENTIX
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-1.5-flash
DEBUG=false
SECRET_KEY=change-this-to-a-secure-random-string
```

### 3. Build and Run

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Docker Commands Reference

### Basic Operations

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Check service status
docker-compose ps
```

### Building

```bash
# Build/rebuild images
docker-compose build

# Build without cache
docker-compose build --no-cache

# Build specific service
docker-compose build backend
```

### Cleanup

```bash
# Stop and remove containers
docker-compose down

# Stop and remove containers, volumes, and images
docker-compose down -v --rmi all

# Remove all unused containers, networks, images
docker system prune -a
```

## Architecture

The Docker setup consists of:

```
┌─────────────────────────────────────────┐
│         Docker Compose Network          │
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │   Frontend   │    │   Backend    │  │
│  │  (Next.js)   │◄──►│  (FastAPI)   │  │
│  │  Port: 3000  │    │  Port: 8000  │  │
│  └──────────────┘    └──────────────┘  │
│         │                    │          │
└─────────┼────────────────────┼──────────┘
          │                    │
     Host:3000            Host:8000
```

### Services

1. **Backend** (`inventix-backend`)
   - Python 3.11-slim base image
   - FastAPI + Uvicorn
   - Exposes port 8000
   - Health check enabled
   - Data persistence via volume

2. **Frontend** (`inventix-frontend`)
   - Node 20-alpine base image
   - Next.js standalone build
   - Exposes port 3000
   - Depends on backend health

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key (required) | - |
| `GEMINI_MODEL` | Gemini model to use | `gemini-1.5-flash` |
| `DEBUG` | Enable debug mode | `false` |
| `SECRET_KEY` | JWT secret key | `inventix-dev-secret-key` |
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

### Port Mapping

Default ports can be changed in `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8000:8000"  # Change left side for host port
  
  frontend:
    ports:
      - "3000:3000"  # Change left side for host port
```

## Production Deployment

### Security Best Practices

1. **Change Default Secrets**
   ```env
   SECRET_KEY=$(openssl rand -hex 32)
   ```

2. **Disable Debug Mode**
   ```env
   DEBUG=false
   ```

3. **Use HTTPS** (with reverse proxy like Nginx)
   ```nginx
   server {
       listen 443 ssl;
       server_name yourdomain.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           proxy_pass http://localhost:3000;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
       }
   }
   ```

4. **Limit Resource Usage**
   Add to `docker-compose.yml`:
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '1'
             memory: 1G
   ```

### Persistent Data

The backend uses a volume for data persistence:

```yaml
volumes:
  - ./backend/data:/app/data
```

Backup this directory regularly:

```bash
# Backup
tar -czf inventix-backup-$(date +%Y%m%d).tar.gz backend/data/

# Restore
tar -xzf inventix-backup-20260201.tar.gz
```

## Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Find process using port 3000
lsof -i :3000

# Change port in docker-compose.yml
ports:
  - "3001:3000"
```

**2. Build Failures**
```bash
# Clear Docker cache
docker-compose down
docker system prune -a
docker-compose build --no-cache
```

**3. Backend Health Check Failing**
```bash
# Check backend logs
docker-compose logs backend

# Verify environment variables
docker-compose exec backend env | grep GEMINI_API_KEY
```

**4. Frontend Can't Connect to Backend**
```bash
# Check network connectivity
docker-compose exec frontend ping backend

# Verify NEXT_PUBLIC_API_URL in frontend
docker-compose exec frontend env | grep API_URL
```

### Debug Mode

Run services in foreground for debugging:

```bash
# Stop background services
docker-compose down

# Run with logs visible
docker-compose up
```

### Shell Access

Access container shells:

```bash
# Backend container
docker-compose exec backend bash

# Frontend container
docker-compose exec frontend sh
```

## Monitoring

### Health Checks

Check service health:

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health (requires implementation)
curl http://localhost:3000/

# Docker health status
docker-compose ps
```

### Resource Usage

Monitor container resources:

```bash
# Real-time stats
docker stats

# Specific service stats
docker stats inventix-backend inventix-frontend
```

## Updates and Maintenance

### Updating the Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d

# Or use one command
docker-compose up -d --build
```

### Viewing Application Logs

```bash
# All logs
docker-compose logs

# Last 100 lines
docker-compose logs --tail=100

# Follow logs
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Docker Build

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker images
        run: docker-compose build
      
      - name: Run tests
        run: |
          docker-compose up -d
          docker-compose exec -T backend pytest
          docker-compose down
```

## Alternative Deployment Options

### Docker Swarm

```bash
docker swarm init
docker stack deploy -c docker-compose.yml inventix
```

### Kubernetes

Convert docker-compose.yml to Kubernetes manifests:

```bash
kompose convert -f docker-compose.yml
kubectl apply -f .
```

## Support

For issues and questions:
- Check logs: `docker-compose logs`
- GitHub Issues: [repository-issues-url]
- Documentation: See main README.md

---

**Note**: Always ensure your `.env` file contains valid credentials and is never committed to version control.
