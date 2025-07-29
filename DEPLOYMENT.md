# Deployment Guide

This guide covers deployment strategies for both Development/Testing and Production environments.

## Overview

The application supports two deployment modes:
- **Development/Testing**: Uses Docker PostgreSQL + Local Excel files
- **Production**: Uses Cloud PostgreSQL + S3 storage

## Development/Testing Environment

### Prerequisites
- Docker and Docker Compose installed
- Python 3.13 installed
- Git installed

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/feniks-pham/trung-nguyen-chatbot
   cd trung-nguyen-chatbot
   ```

2. **Setup environment file (required before running setup script)**
   ```bash
   cp env.dev.example .env
   # Edit .env with your configurations (API keys, database, etc.)
   ```

3. **Run the dev setup script**
   ```bash
   chmod +x scripts/dev-setup.sh
   ./scripts/dev-setup.sh
   ```


4. **Start the application**
   ```bash
   # Backend (in terminal 1)
   ./start.sh
   
   # Frontend (in terminal 2)
   source venv/bin/activate
   streamlit run frontend/streamlit_app.py
   ```

### Manual Development Setup

If you prefer manual setup:

1. **Setup environment file**
   ```bash
   cp env.dev.example .env
   # Edit .env with your configurations
   ```

2. **Start PostgreSQL**
   ```bash
   # For Docker Compose v2+ (integrated plugin)
   docker compose -f docker-compose.dev.yml up -d postgres
   
   # For Docker Compose v1 (standalone)
   docker-compose -f docker-compose.dev.yml up -d postgres
   ```

3. **Create virtual environment**
   ```bash
   python3.13 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Index knowledge base**
   ```bash
   python scripts/import_qa_data.py
   ```

### Development Configuration

The dev environment uses:
- **Database**: PostgreSQL in Docker container
- **Data Source**: Local Excel file (`data/trung-nguyen-legend.xlsx`)
- **Environment**: `APP_ENV=dev`

Key settings in `.env`:
```env
APP_ENV=dev
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/trung_nguyen_chatbot
LOCAL_DATA_FILE=data/trung-nguyen-legend.xlsx
```

### Development Commands

```bash
# Start database only
# For Docker Compose v2+ (integrated plugin)
docker compose -f docker-compose.dev.yml up -d postgres
# For Docker Compose v1 (standalone)
docker-compose -f docker-compose.dev.yml up -d postgres

# Stop database
# For Docker Compose v2+ (integrated plugin)
docker compose -f docker-compose.dev.yml down
# For Docker Compose v1 (standalone)
docker-compose -f docker-compose.dev.yml down

# Re-index knowledge base
python scripts/import_qa_data.py

# View database logs
# For Docker Compose v2+ (integrated plugin)
docker compose -f docker-compose.dev.yml logs -f postgres
# For Docker Compose v1 (standalone)
docker-compose -f docker-compose.dev.yml logs -f postgres
```

## Production Environment

### Prerequisites
- PostgreSQL database (cloud or self-hosted)
- S3-compatible storage with Excel file uploaded
- Python 3.13
- All production API keys and configurations

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/feniks-pham/trung-nguyen-chatbot
   cd trung-nguyen-chatbot
   ```

2. **Setup environment file (required before running setup script)**
   ```bash
   cp env.prod.example .env
   # Edit .env with your production configurations (API keys, S3, database, etc.)
   ```

3. **Run the prod setup script**
   ```bash
   chmod +x scripts/prod-setup.sh
   ./scripts/prod-setup.sh
   ```

4. **Start the application**
   ```bash
   # Backend (in terminal 1)
   ./start.sh
   
   # Frontend (in terminal 2)
   source venv/bin/activate
   streamlit run frontend/streamlit_app.py

### Manual Production Setup

1. **Setup environment file**
   ```bash
   cp env.prod.example .env
   # Edit .env with your production configurations
   ```

2. **Create virtual environment**
   ```bash
   python3.13 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Initialize database**
   ```bash
   psql $DATABASE_URL -f scripts/init_db.sql
   ```

4. **Index knowledge base from S3**
   ```bash
   python scripts/import_qa_data.py
   ```

### Production Configuration

The production environment uses:
- **Database**: Cloud PostgreSQL with pgvector extension
- **Data Source**: S3-compatible storage
- **Environment**: `APP_ENV=prod`

Key settings in `.env`:
```env
APP_ENV=prod
DATABASE_URL=postgresql://user:pass@host:5432/dbname
S3_PATH=your-bucket-name
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_ENDPOINT_URL=your-s3-endpoint
S3_EXCEL_FILE_KEY=path/to/your/excel/file.xlsx
```

### Kubernetes Deployment

For Kubernetes deployment:

1. **Create ConfigMap for non-sensitive configs**
   ```bash
   kubectl create configmap chatbot-config \
     --from-literal=APP_ENV=prod \
     --from-literal=LOG_LEVEL=INFO \
     --from-literal=S3_PATH=your-bucket
   ```

2. **Create Secret for sensitive data**
   ```bash
   kubectl create secret generic chatbot-secret \
     --from-literal=DATABASE_URL=postgresql://... \
     --from-literal=LLM_API_KEY=your-key \
     --from-literal=AWS_ACCESS_KEY_ID=your-key \
     --from-literal=AWS_SECRET_ACCESS_KEY=your-secret
   ```

3. **Deploy the application**
   ```bash
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   kubectl apply -f k8s/ingress.yaml
   ```

## Environment Variables Reference

### Required for All Environments
- `APP_ENV`: Environment type (dev/prod)
- `DATABASE_URL`: PostgreSQL connection string
- `LLM_API_URL`, `LLM_API_KEY`: LLM service configuration
- `EMBEDDING_API_URL`, `EMBEDDING_API_KEY`: Embedding service configuration
- `TTS_API_URL`, `TTS_API_KEY`: Text-to-speech service configuration

### Development Only
- `LOCAL_DATA_FILE`: Path to local Excel file

### Production Only
- `S3_PATH`: S3 bucket name
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`: AWS credentials
- `S3_ENDPOINT_URL`: S3 endpoint URL
- `S3_EXCEL_FILE_KEY`: Path to Excel file in S3

## Troubleshooting

### Common Issues

1. **Database connection failed**
   - Check if PostgreSQL is running
   - Verify DATABASE_URL format
   - Ensure database exists and has pgvector extension

2. **S3 connection failed (Production)**
   - Verify S3 credentials and endpoint
   - Check if bucket exists and is accessible
   - Ensure Excel file exists at specified key

3. **Local file not found (Development)**
   - Ensure `data/trung-nguyen-legend.xlsx` exists
   - Check file permissions

4. **Import script fails**
   - Check if all API keys are configured
   - Verify database schema is initialized
   - Check logs for specific error messages

### Logs and Monitoring

```bash
# View application logs
tail -f logs/app.log

# View database logs (dev)
# For Docker Compose v2+ (integrated plugin)
docker compose -f docker-compose.dev.yml logs -f postgres
# For Docker Compose v1 (standalone)
docker-compose -f docker-compose.dev.yml logs -f postgres

# Check database connection
python -c "
from app.config.settings import settings
print(f'Environment: {settings.app_env}')
print(f'Database: {settings.database_url}')
"
```

## Security Considerations

1. **Environment Files**
   - Never commit `.env` files to version control
   - Use different credentials for dev/prod
   - Store production secrets in secure secret management

2. **Database Security**
   - Use SSL connections in production
   - Implement proper firewall rules
   - Regular security updates

3. **API Keys**
   - Rotate keys regularly
   - Use least privilege access
   - Monitor API usage

## Performance Optimization

1. **Database**
   - Regular VACUUM and ANALYZE
   - Monitor connection pool usage
   - Optimize vector search queries

2. **Application**
   - Monitor memory usage during embedding
   - Implement proper caching
   - Use async operations where possible

3. **S3 (Production)**
   - Use CloudFront for better performance
   - Implement proper caching policies
   - Monitor transfer costs 