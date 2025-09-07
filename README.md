# 🚀 AI Studio - Production-Ready Multimodal AI Platform

A comprehensive, production-ready AI studio built with FastAPI, Vue.js, and state-of-the-art small language models. Features multimodal capabilities, RAG (Retrieval-Augmented Generation), fine-tuning, agent orchestration, and real-time processing.

## ✨ Features

### 🤖 **Multi-Agent Architecture**
- **Code Agent**: Specialized code generation, review, and explanation
- **Text Agent**: Creative writing, summarization, and analysis  
- **RAG Agent**: Document-based question answering with context retrieval
- **Agent Orchestrator**: Intelligent task distribution and load balancing

### 🧠 **Advanced AI Capabilities**
- **Small, Efficient Models**: Phi-2, T5-Small, MiniLM for optimal performance
- **Fine-tuning Support**: LoRA-based fine-tuning for domain specialization
- **Quantization**: 4-bit quantization for memory efficiency
- **Domain Specialization**: Code, creative, analysis, summarization domains

### 🔍 **RAG (Retrieval-Augmented Generation)**
- **Document Ingestion**: PDF, DOCX, TXT, JSON support
- **Vector Search**: FAISS-based semantic search
- **Context Enhancement**: Automatic context retrieval for queries
- **Citation Tracking**: Source attribution for generated responses

### 🎙️ **Multimodal Processing**
- **Voice-to-Text**: Whisper-based speech recognition
- **Image Analysis**: CLIP-based image understanding
- **Audio Processing**: Real-time transcription
- **File Upload**: Multi-format document processing

### 🛠️ **Development Tools**
- **Code Canvas**: Interactive code editor with live preview
- **Template System**: Pre-built prompts for common tasks
- **Streaming Responses**: Real-time response generation
- **Model Switching**: Dynamic model selection

### 📊 **Production Features**
- **Monitoring**: Prometheus metrics and Grafana dashboards
- **Logging**: Structured logging with correlation IDs
- **Health Checks**: Comprehensive service health monitoring
- **Auto-scaling**: Container orchestration ready
- **Backup/Restore**: Automated data backup systems

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   AI Services   │
│   (Vue.js)      │◄──►│   (FastAPI)     │◄──►│   (PyTorch)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx         │    │   PostgreSQL    │    │   Redis Cache   │
│   (Proxy)       │    │   (Metadata)    │    │   (Sessions)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Monitoring    │    │   Task Queue    │    │   File Storage  │
│   (Grafana)     │    │   (Celery)      │    │   (Volumes)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- 4GB+ RAM recommended
- NVIDIA GPU (optional, for acceleration)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-studio.git
cd ai-studio
```

### 2. Development Setup
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Start development environment
./scripts/start_dev.sh
```

### 3. Production Deployment
```bash
# Deploy with Docker Compose
./scripts/deploy_production.sh
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Monitoring**: http://localhost:3001 (Grafana)
- **Task Monitor**: http://localhost:5555 (Flower)

## 📖 Usage Guide

### Basic Chat
```python
# Send a message
POST /api/chat-text/
{
    "messages": [{"role": "user", "content": "Write a Python function"}],
    "domain": "code",
    "temperature": 0.7
}
```

### RAG-Enhanced Chat
```python
# Upload documents first
POST /api/chat-rag/upload-documents
# Form data with files

# Query with context
POST /api/chat-rag/
{
    "messages": [{"role": "user", "content": "What does the document say about AI?"}],
    "use_rag": true
}
```

### Voice Processing
```python
# Transcribe audio
POST /api/voice/transcribe
# Form data with audio file
```

### Fine-tuning
```python
# Start fine-tuning job
POST /api/fine-tuning/
{
    "adapter_name": "my_specialist",
    "training_data": [...],
    "lora_config": {"r": 16, "lora_alpha": 32}
}
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```bash
# Server
HOST=0.0.0.0
PORT=8000
WORKERS=1
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://user:pass@localhost/ai_studio

# Redis
REDIS_URL=redis://localhost:6379/0

# AI Models
MODEL_CACHE_DIR=./models
RAG_STORAGE_DIR=./rag_storage

# Security
SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=http://localhost:3000

# Monitoring
ENABLE_METRICS=true
LOG_LEVEL=INFO
```

#### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=AI Studio
VITE_APP_VERSION=1.0.0
```

### Model Configuration

The system uses optimized small models:

- **Text Generation**: Microsoft Phi-2 (2.7B parameters)
- **Code Generation**: CodeT5p-220M
- **Embeddings**: all-MiniLM-L6-v2
- **Speech**: Whisper-tiny
- **Vision**: CLIP-ViT-B-16

## 📊 Monitoring

### Health Checks
```bash
# Check system health
curl http://localhost:8000/health

# Check model status
curl http://localhost:8000/models/status

# Check metrics
curl http://localhost:8000/metrics
```

### Grafana Dashboards

Pre-configured dashboards for:
- API Response Times
- Model Inference Metrics
- System Resource Usage
- Error Rates and Success Rates
- Agent Performance

## 🛠️ Development

### Project Structure
```
ai-studio/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── services/     # Business logic
│   │   ├── models/       # Data models
│   │   └── core/         # Configuration
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/   # Vue components
│   │   ├── views/        # Pages
│   │   ├── store/        # State management
│   │   └── api/          # API client
│   ├── package.json
│   └── Dockerfile
├── scripts/              # Deployment scripts
├── docker-compose.yml
└── README.md
```

### Adding New Models
1. Update `ModelManager` in `services/model_manager.py`
2. Add model configuration
3. Implement loading and inference logic
4. Update API endpoints

### Adding New Agents
1. Extend `BaseAgent` class
2. Implement required methods
3. Register with `AgentOrchestrator`
4. Add API endpoints

### Custom Fine-tuning
```python
from app.services.llm import llm_service

# Prepare training data
training_data = [
    {
        "messages": [
            {"role": "user", "content": "input"},
            {"role": "assistant", "content": "output"}
        ],
        "domain": "custom"
    }
]

# Start fine-tuning
result = await llm_service.fine_tune_lora(
    training_data=training_data,
    adapter_name="custom_adapter",
    lora_config={
        "r": 16,
        "lora_alpha": 32,
        "lora_dropout": 0.1
    }
)
```

## 🔐 Security

### Authentication
- JWT-based authentication (optional)
- API key authentication
- Rate limiting per IP/user

### Data Protection
- Input sanitization
- SQL injection prevention
- XSS protection
- CORS configuration

### Model Security
- Model weight validation
- Inference timeout limits
- Memory usage monitoring
- Sandboxed execution

## 📈 Performance

### Optimization Features
- **Model Quantization**: 4-bit quantization reduces memory by 75%
- **Caching**: Redis-based response caching
- **Batching**: Request batching for efficiency
- **Load Balancing**: Multi-worker deployment
- **Memory Management**: Automatic cleanup and optimization

### Benchmarks
- **Response Time**: <2s for most queries
- **Memory Usage**: <4GB with quantization
- **Throughput**: 10+ concurrent requests
- **Model Loading**: <30s cold start

## 🐛 Troubleshooting

### Common Issues

#### Backend not starting
```bash
# Check logs
./scripts/logs.sh api

# Verify models are downloading
docker-compose exec api ls -la /app/models
```

#### Out of memory
```bash
# Enable quantization
export ENABLE_QUANTIZATION=true

# Reduce batch size
export MAX_BATCH_SIZE=1
```

#### RAG not working
```bash
# Check document upload
curl -X POST -F "files=@document.pdf" http://localhost:8000/api/chat-rag/upload-documents

# Verify vector index
./scripts/shell.sh api
python -c "from app.services.rag_engine import rag_engine; print(rag_engine.get_stats())"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Setup
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Frontend
cd frontend
npm install
npm run dev
```

### Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

## 📝 License

This project is licensed under the MIT License 

## 🙏 Acknowledgments

- **Hugging Face** for transformer models and libraries
- **FastAPI** for the excellent web framework
- **Vue.js** for the reactive frontend framework
- **Microsoft** for the Phi-2 model
- **OpenAI** for Whisper and CLIP models


---

**Built with ❤️ for the AI community**