# scripts/start_dev.sh
#!/bin/bash

echo "🚀 Starting AI Studio Development Environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create necessary directories
mkdir -p logs models rag_storage

# Set environment variables
export ENVIRONMENT=development
export DEBUG=true

# Start backend services
echo "📦 Starting backend services..."
cd backend

# Install dependencies if not already installed
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate

# Install requirements
pip install -r requirements.txt

# Start the backend server
echo "🖥️ Starting FastAPI server..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to be ready
echo "⏳ Waiting for backend to start..."
sleep 10

# Start frontend
echo "🎨 Starting frontend..."
cd ../frontend

# Install dependencies if not already installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start the frontend development server
npm run dev &
FRONTEND_PID=$!

echo "✅ AI Studio is starting up!"
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt signal
trap "echo '🛑 Shutting down...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait

# scripts/deploy_production.sh
#!/bin/bash

echo "🚀 Deploying AI Studio to Production..."

# Build and start with Docker Compose
echo "🔨 Building Docker images..."
docker-compose build --no-cache

echo "🏃 Starting production services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
curl -f http://localhost:8000/health || echo "⚠️ Backend health check failed"
curl -f http://localhost:3000 || echo "⚠️ Frontend health check failed"

echo "✅ Deployment complete!"
echo "🌐 Application: http://localhost"
echo "🔧 API: http://localhost:8000"
echo "📊 Monitoring: http://localhost:3001 (Grafana)"
echo "🌸 Task Monitor: http://localhost:5555 (Flower)"

# scripts/backup.sh  
#!/bin/bash

echo "💾 Creating AI Studio backup..."

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backup_${DATE}"

mkdir -p $BACKUP_DIR

# Backup database
echo "📦 Backing up database..."
docker-compose exec postgres pg_dump -U postgres ai_studio > $BACKUP_DIR/database.sql

# Backup RAG storage
echo "📁 Backing up RAG storage..."
docker cp $(docker-compose ps -q api):/app/rag_storage $BACKUP_DIR/

# Backup model cache
echo "🤖 Backing up model cache..."
docker cp $(docker-compose ps -q api):/app/models $BACKUP_DIR/

# Create archive
tar -czf "ai_studio_backup_${DATE}.tar.gz" $BACKUP_DIR
rm -rf $BACKUP_DIR

echo "✅ Backup created: ai_studio_backup_${DATE}.tar.gz"

# scripts/restore.sh
#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: ./restore.sh <backup_file.tar.gz>"
    exit 1
fi

BACKUP_FILE=$1
TEMP_DIR="restore_temp"

echo "🔄 Restoring AI Studio from backup: $BACKUP_FILE"

# Extract backup
tar -xzf $BACKUP_FILE
BACKUP_DIR=$(tar -tzf $BACKUP_FILE | head -1 | cut -f1 -d"/")

# Stop services
echo "⏹️ Stopping services..."
docker-compose down

# Restore database
echo "🗃️ Restoring database..."
docker-compose up -d postgres
sleep 10
cat $BACKUP_DIR/database.sql | docker-compose exec -T postgres psql -U postgres ai_studio

# Restore files
echo "📁 Restoring files..."
docker-compose up -d api
sleep 10
docker cp $BACKUP_DIR/rag_storage $(docker-compose ps -q api):/app/
docker cp $BACKUP_DIR/models $(docker-compose ps -q api):/app/

# Restart all services
echo "🚀 Starting all services..."
docker-compose up -d

# Cleanup
rm -rf $BACKUP_DIR

echo "✅ Restore complete!"

# scripts/update.sh
#!/bin/bash

echo "🔄 Updating AI Studio..."

# Pull latest changes
git pull origin main

# Rebuild and restart services
echo "🔨 Rebuilding services..."
docker-compose down
docker-compose build --no-cache
docker-compose up -d

echo "✅ Update complete!"

# scripts/logs.sh
#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: ./logs.sh <service_name>"
    echo "Available services: api, frontend, postgres, redis, celery_worker"
    exit 1
fi

SERVICE=$1
echo "📋 Showing logs for $SERVICE..."
docker-compose logs -f $SERVICE

# scripts/shell.sh
#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: ./shell.sh <service_name>"
    echo "Available services: api, frontend, postgres, redis"
    exit 1
fi

SERVICE=$1
echo "🐚 Opening shell for $SERVICE..."

case $SERVICE in
    "api")
        docker-compose exec api /bin/bash
        ;;
    "postgres")
        docker-compose exec postgres psql -U postgres ai_studio
        ;;
    "redis")
        docker-compose exec redis redis-cli
        ;;
    *)
        docker-compose exec $SERVICE /bin/sh
        ;;
esac