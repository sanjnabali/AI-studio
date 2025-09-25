# AI Studio - Production-Ready AI Development Platform

A comprehensive AI development platform similar to Google AI Studio, built with FastAPI (Python) and Vue 3 (TypeScript).

## 🚀 Features

### Core AI Capabilities
- **Multi-Modal Chat**: Text, voice, and image conversations with AI
- **RAG (Retrieval-Augmented Generation)**: Upload and query documents (PDF, DOCX, TXT)
- **Code Generation & Execution**: Generate, run, and analyze code in multiple languages
- **Voice Processing**: Speech-to-text and text-to-speech using real AI models
- **Image Analysis**: AI-powered image understanding and description

### Advanced Features
- **Real-time Code Canvas**: Interactive coding environment with live execution
- **Document Intelligence**: Smart document processing and question-answering
- **Voice Conversations**: Natural speech interactions with AI
- **Model Configuration**: Fine-tune AI parameters (temperature, top-p, etc.)
- **Session Management**: Persistent chat sessions and conversation history
- **Secure Authentication**: JWT-based auth with password hashing

### Technical Excellence
- **Production-Ready Security**: Password validation, API key management, secure file uploads
- **Scalable Architecture**: Modular design with proper error handling
- **Real AI Models**: Uses Transformers, Whisper, SpeechT5, and other pre-trained models
- **Database Integration**: SQLAlchemy with session management
- **Vector Database**: ChromaDB for efficient document similarity search
- **Modern Frontend**: Vue 3 + TypeScript + Tailwind CSS + DaisyUI

## 🛠 Technology Stack

### Backend
- **FastAPI** - High-performance web framework
- **SQLAlchemy** - Database ORM
- **ChromaDB** - Vector database for RAG
- **Transformers** - Hugging Face models
- **Whisper** - Speech recognition
- **SpeechT5** - Text-to-speech
- **JWT** - Authentication
- **Docker** - Containerization

### Frontend
- **Vue 3** - Progressive web framework
- **TypeScript** - Type-safe JavaScript
- **Pinia** - State management
- **Tailwind CSS** - Utility-first styling
- **DaisyUI** - Component library
- **Axios** - HTTP client

### AI Models (Pre-trained, No APIs)
- **DialoGPT**: Conversational AI
- **CodeBERT**: Code understanding
- **Whisper**: Speech-to-text
- **SpeechT5**: Text-to-speech
- **BART**: Text summarization
- **Sentence-Transformers**: Embeddings

## 📦 Installation

### Prerequisites
- Python 3.8+ 
- Node.js 16+
- Docker (optional)

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/sanjnabali/ai-studio.git
cd ai-studio
```

2. **Start development environment**
```bash
chmod +x scripts/start_dev.sh
./scripts/start_dev.sh
```

This will automatically:
- Set up Python virtual environment
- Install all dependencies
- Start backend on http://localhost:8000
- Start frontend on http://localhost:5173

3. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Manual Setup

#### Backend Setup
```bash
cd Backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Edit with your configuration
uvicorn app.main:app --reload
```

#### Frontend Setup
```bash
cd Frontend
npm install
npm run dev
```

### Docker Setup
```bash
docker-compose up -d
```

## 🔧 Configuration

### Environment Variables (.env)
```env
SECRET_KEY=your-super-secret-key
DATABASE_URL=sqlite:///./ai_studio.db
DEBUG=False
HF_TOKEN=your-huggingface-token  # Optional
MAX_FILE_SIZE=10485760  # 10MB
```

### Model Configuration
The system automatically downloads and caches AI models on first use:
- Models are stored in `~/.cache/huggingface/`
- First startup may take 5-10 minutes to download models
- Subsequent starts are much faster

## 📚 Usage

### 1. Authentication
- Register a new account or login
- Secure JWT-based authentication
- API key generation for programmatic access

### 2. Chat Interface
- Start conversations with AI
- Upload documents for RAG-based Q&A
- Voice input/output support
- Configurable model parameters

### 3. Code Canvas
- Generate code from natural language
- Execute code in multiple languages
- Real-time analysis and suggestions
- Interactive debugging

### 4. Document Processing
- Upload PDF, DOCX, TXT files
- Automatic chunking and embedding
- Smart search and retrieval
- Citation tracking

### 5. Voice Features
- Record voice messages
- AI speech recognition
- Text-to-speech output
- Natural conversations

## 🏗 Architecture

```
AI-STUDIO/
├── Backend/           # FastAPI application
│   ├── app/
│   │   ├── api/       # API endpoints
│   │   ├── core/      # Security, config
│   │   ├── models/    # Database models
│   │   └── services/  # Business logic
│   ├── requirements.txt
│   └── Dockerfile
├── Frontend/          # Vue.js application
│   ├── src/
│   │   ├── components/  # Vue components
│   │   ├── store/      # Pinia stores
│   │   ├── api/        # API client
│   │   └── views/      # Page components
│   ├── package.json
│   └── Dockerfile
├── scripts/           # Deployment scripts
└── docker-compose.yml
```

## 🔒 Security Features

- **Password Hashing**: Bcrypt encryption
- **JWT Authentication**: Secure token-based auth
- **CORS Protection**: Configurable origins
- **File Upload Security**: Type and size validation
- **SQL Injection Prevention**: SQLAlchemy ORM
- **XSS Protection**: Input sanitization
- **Rate Limiting**: Request throttling
- **Secure Headers**: Security middleware

## 🚀 Deployment

### Development
```bash
./scripts/start_dev.sh
```

### Production
```bash
./scripts/deploy_production.sh
```

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Performance

- **Model Loading**: Optimized caching and lazy loading
- **Memory Management**: Efficient model sharing
- **Database**: Connection pooling and query optimization
- **Frontend**: Code splitting and lazy loading
- **File Processing**: Streaming uploads and chunked processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Models not downloading**
   - Check internet connection
   - Verify HuggingFace token (if using private models)
   - Check disk space (models can be 1-2GB each)

2. **Voice features not working**
   - Enable microphone permissions
   - Check browser compatibility
   - Install audio system dependencies

3. **Code execution failing**
   - Ensure Python/Node.js are installed
   - Check security settings
   - Verify Docker access (if using containers)

### Performance Tips
- Use GPU acceleration if available
- Increase memory allocation for large documents
- Enable model quantization for faster inference
- Use SSD storage for better model loading

## 🔮 Roadmap

- [ ] Multi-language support
- [ ] Advanced RAG features
- [ ] More AI model options
- [ ] Collaborative features
- [ ] Mobile app
- [ ] Cloud deployment templates
- [ ] Advanced analytics
- [ ] Plugin system

---

**Built with ❤️ for the AI community**