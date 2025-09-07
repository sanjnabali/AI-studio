#!/bin/bash

# AI Studio - Google Cloud Run Deployment Script
# This script deploys the AI Studio application to Google Cloud Run

set -e  # Exit on any error

# Configuration
PROJECT_ID=${PROJECT_ID:-"ai-studio-prod"}
REGION=${REGION:-"us-central1"}
SERVICE_NAME=${SERVICE_NAME:-"ai-studio"}
BACKEND_SERVICE_NAME="ai-studio-backend"
FRONTEND_SERVICE_NAME="ai-studio-frontend"
REGISTRY_URL="gcr.io"
MEMORY=${MEMORY:-"4Gi"}
CPU=${CPU:-"2"}
MAX_INSTANCES=${MAX_INSTANCES:-"10"}
MIN_INSTANCES=${MIN_INSTANCES:-"1"}
CONCURRENCY=${CONCURRENCY:-"10"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    echo_info "Checking prerequisites..."
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        echo_error "gcloud CLI is not installed. Please install it first."
        echo "Visit: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        echo_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    # Check if user is authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
        echo_error "Please authenticate with gcloud first: gcloud auth login"
        exit 1
    fi
    
    echo_success "Prerequisites check passed"
}

# Setup Google Cloud project
setup_project() {
    echo_info "Setting up Google Cloud project: $PROJECT_ID"
    
    # Set project
    gcloud config set project $PROJECT_ID
    
    # Enable required APIs
    echo_info "Enabling required APIs..."
    gcloud services enable \
        cloudbuild.googleapis.com \
        run.googleapis.com \
        containerregistry.googleapis.com \
        sql-component.googleapis.com \
        redis.googleapis.com \
        secretmanager.googleapis.com \
        --project=$PROJECT_ID
    
    echo_success "Project setup complete"
}

# Create Cloud SQL instance for PostgreSQL
create_database() {
    echo_info "Setting up Cloud SQL PostgreSQL instance..."
    
    DB_INSTANCE_NAME="ai-studio-db"
    DB_PASSWORD=$(openssl rand -base64 32)
    
    # Check if instance already exists
    if gcloud sql instances describe $DB_INSTANCE_NAME --project=$PROJECT_ID &>/dev/null; then
        echo_warning "Database instance $DB_INSTANCE_NAME already exists"
    else
        echo_info "Creating Cloud SQL instance..."
        gcloud sql instances create $DB_INSTANCE_NAME \
            --database-version=POSTGRES_15 \
            --tier=db-f1-micro \
            --region=$REGION \
            --storage-type=SSD \
            --storage-size=10GB \
            --backup \
            --project=$PROJECT_ID
    fi
    
    # Create database
    gcloud sql databases create ai_studio \
        --instance=$DB_INSTANCE_NAME \
        --project=$PROJECT_ID || true
    
    # Store database password in Secret Manager
    echo -n "$DB_PASSWORD" | gcloud secrets create db-password \
        --data-file=- \
        --project=$PROJECT_ID || true
    
    echo_success "Database setup complete"
}

# Create Redis instance
create_redis() {
    echo_info "Setting up Redis instance..."
    
    REDIS_INSTANCE_NAME="ai-studio-cache"
    
    # Check if instance already exists
    if gcloud redis instances describe $REDIS_INSTANCE_NAME --region=$REGION --project=$PROJECT_ID &>/dev/null; then
        echo_warning "Redis instance $REDIS_INSTANCE_NAME already exists"
    else
        echo_info "Creating Redis instance..."
        gcloud redis instances create $REDIS_INSTANCE_NAME \
            --size=1 \
            --region=$REGION \
            --redis-version=redis_6_x \
            --project=$PROJECT_ID
    fi
    
    echo_success "Redis setup complete"
}

# Build and push Docker images
build_and_push_images() {
    echo_info "Building and pushing Docker images..."
    
    # Configure Docker to use gcloud as credential helper
    gcloud auth configure-docker --project=$PROJECT_ID
    
    # Build backend image
    echo_info "Building backend image..."
    docker build -t $REGISTRY_URL/$PROJECT_ID/$BACKEND_SERVICE_NAME:latest ./backend
    docker push $REGISTRY_URL/$PROJECT_ID/$BACKEND_SERVICE_NAME:latest
    
    # Build frontend image
    echo_info "Building frontend image..."
    docker build -t $REGISTRY_URL/$PROJECT_ID/$FRONTEND_SERVICE_NAME:latest ./frontend
    docker push $REGISTRY_URL/$PROJECT_ID/$FRONTEND_SERVICE_NAME:latest
    
    echo_success "Docker images built and pushed"
}

# Deploy backend service to Cloud Run
deploy_backend() {
    echo_info "Deploying backend service to Cloud Run..."
    
    # Get database connection name
    DB_CONNECTION_NAME=$(gcloud sql instances describe ai-studio-db --project=$PROJECT_ID --format="value(connectionName)")
    
    # Get Redis host
    REDIS_HOST=$(gcloud redis instances describe ai-studio-cache --region=$REGION --project=$PROJECT_ID --format="value(host)")
    
    # Deploy backend service
    gcloud run deploy $BACKEND_SERVICE_NAME \
        --image=$REGISTRY_URL/$PROJECT_ID/$BACKEND_SERVICE_NAME:latest \
        --platform=managed \
        --region=$REGION \
        --allow-unauthenticated \
        --memory=$MEMORY \
        --cpu=$CPU \
        --min-instances=$MIN_INSTANCES \
        --max-instances=$MAX_INSTANCES \
        --concurrency=$CONCURRENCY \
        --timeout=3600 \
        --set-env-vars="ENVIRONMENT=production,HOST=0.0.0.0,PORT=8000" \
        --set-env-vars="DATABASE_URL=postgresql://postgres@/$PROJECT_ID:$REGION:ai-studio-db/ai_studio" \
        --set-env-vars="REDIS_URL=redis://$REDIS_HOST:6379/0" \
        --set-env-vars="ALLOWED_ORIGINS=*" \
        --add-cloudsql-instances=$DB_CONNECTION_NAME \
        --project=$PROJECT_ID
    
    # Get backend service URL
    BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)")
    
    echo_success "Backend deployed: $BACKEND_URL"
}

# Deploy frontend service to Cloud Run
deploy_frontend() {
    echo_info "Deploying frontend service to Cloud Run..."
    
    # Get backend URL
    BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)")
    
    # Deploy frontend service
    gcloud run deploy $FRONTEND_SERVICE_NAME \
        --image=$REGISTRY_URL/$PROJECT_ID/$FRONTEND_SERVICE_NAME:latest \
        --platform=managed \
        --region=$REGION \
        --allow-unauthenticated \
        --memory=512Mi \
        --cpu=1 \
        --min-instances=0 \
        --max-instances=5 \
        --concurrency=80 \
        --set-env-vars="VITE_API_BASE_URL=$BACKEND_URL" \
        --project=$PROJECT_ID
    
    # Get frontend service URL
    FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)")
    
    echo_success "Frontend deployed: $FRONTEND_URL"
}

# Setup Cloud Load Balancer (optional)
setup_load_balancer() {
    echo_info "Setting up Cloud Load Balancer..."
    
    # Create load balancer components
    LB_NAME="ai-studio-lb"
    
    # Create health check
    gcloud compute health-checks create http $LB_NAME-health-check \
        --port=8080 \
        --request-path=/health \
        --project=$PROJECT_ID || true
    
    # Create backend service
    gcloud compute backend-services create $LB_NAME-backend \
        --protocol=HTTP \
        --health-checks=$LB_NAME-health-check \
        --global \
        --project=$PROJECT_ID || true
    
    echo_success "Load balancer setup complete"
}

# Setup monitoring and logging
setup_monitoring() {
    echo_info "Setting up monitoring and logging..."
    
    # Create log sink for structured logs
    gcloud logging sinks create ai-studio-logs \
        bigquery.googleapis.com/projects/$PROJECT_ID/datasets/ai_studio_logs \
        --log-filter='resource.type="cloud_run_revision" AND resource.labels.service_name=("'$BACKEND_SERVICE_NAME'" OR "'$FRONTEND_SERVICE_NAME'")' \
        --project=$PROJECT_ID || true
    
    # Create alerting policy for high error rate
    cat > alerting-policy.json << EOF
{
  "displayName": "AI Studio High Error Rate",
  "conditions": [{
    "displayName": "High 5xx error rate",
    "conditionThreshold": {
      "filter": "resource.type=\"cloud_run_revision\" AND resource.label.service_name=\"$BACKEND_SERVICE_NAME\"",
      "comparison": "COMPARISON_GT",
      "thresholdValue": 0.1,
      "duration": "300s",
      "aggregations": [{
        "alignmentPeriod": "60s",
        "perSeriesAligner": "ALIGN_RATE",
        "crossSeriesReducer": "REDUCE_MEAN"
      }]
    }
  }],
  "notificationChannels": [],
  "alertStrategy": {
    "autoClose": "1800s"
  }
}
EOF
    
    gcloud alpha monitoring policies create --policy-from-file=alerting-policy.json --project=$PROJECT_ID || true
    rm alerting-policy.json
    
    echo_success "Monitoring setup complete"
}

# Create deployment info
create_deployment_info() {
    echo_info "Creating deployment information..."
    
    BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)")
    FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)")
    
    cat > deployment-info.txt << EOF
🚀 AI Studio Cloud Run Deployment Complete!

📊 Deployment Details:
- Project ID: $PROJECT_ID
- Region: $REGION
- Deployment Time: $(date)

🔗 Service URLs:
- Frontend: $FRONTEND_URL
- Backend API: $BACKEND_URL
- API Documentation: $BACKEND_URL/docs

💾 Infrastructure:
- Database: Cloud SQL PostgreSQL (ai-studio-db)
- Cache: Redis (ai-studio-cache)  
- Container Registry: $REGISTRY_URL/$PROJECT_ID

🔧 Management Commands:
- View logs: gcloud run services logs tail $BACKEND_SERVICE_NAME --project=$PROJECT_ID
- Update backend: gcloud run deploy $BACKEND_SERVICE_NAME --image=$REGISTRY_URL/$PROJECT_ID/$BACKEND_SERVICE_NAME:latest --region=$REGION --project=$PROJECT_ID
- Scale service: gcloud run services update $BACKEND_SERVICE_NAME --max-instances=20 --region=$REGION --project=$PROJECT_ID
- Delete services: gcloud run services delete $BACKEND_SERVICE_NAME --region=$REGION --project=$PROJECT_ID

📈 Monitoring:
- Cloud Console: https://console.cloud.google.com/run?project=$PROJECT_ID
- Logs: https://console.cloud.google.com/logs/query?project=$PROJECT_ID
- Metrics: https://console.cloud.google.com/monitoring?project=$PROJECT_ID

🔐 Security Notes:
- Services are deployed with public access
- Database is private and accessible only via Cloud SQL Proxy
- Redis instance is in VPC and private
- Consider setting up IAM authentication for production
EOF
    
    echo_success "Deployment info saved to deployment-info.txt"
}

# Cleanup function
cleanup_on_error() {
    echo_error "Deployment failed. Cleaning up resources..."
    
    # Delete Cloud Run services
    gcloud run services delete $BACKEND_SERVICE_NAME --region=$REGION --project=$PROJECT_ID --quiet || true
    gcloud run services delete $FRONTEND_SERVICE_NAME --region=$REGION --project=$PROJECT_ID --quiet || true
    
    echo_info "Cleanup complete"
}

# Main deployment function
main() {
    echo_info "🚀 Starting AI Studio deployment to Google Cloud Run..."
    echo_info "Project: $PROJECT_ID | Region: $REGION"
    
    # Set trap for cleanup on error
    trap cleanup_on_error ERR
    
    # Check if running from correct directory
    if [[ ! -f "docker-compose.yml" ]] || [[ ! -d "backend" ]] || [[ ! -d "frontend" ]]; then
        echo_error "Please run this script from the AI Studio root directory"
        exit 1
    fi
    
    # Deployment steps
    check_prerequisites
    setup_project
    create_database
    create_redis
    build_and_push_images
    deploy_backend
    deploy_frontend
    setup_monitoring
    create_deployment_info
    
    echo_success "🎉 Deployment completed successfully!"
    echo_info "Check deployment-info.txt for service URLs and management commands"
    
    # Display key information
    FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)")
    BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)")
    
    echo ""
    echo_success "🌐 Your AI Studio is now live!"
    echo_info "Frontend: $FRONTEND_URL"
    echo_info "Backend: $BACKEND_URL"
    echo_info "API Docs: $BACKEND_URL/docs"
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi