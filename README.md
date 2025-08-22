# 🌌 Astrochat - AI-Powered Horoscope API

A modern, containerized horoscope API that combines traditional astrology with AI-powered insights using vector search and multi-language translation.

## 🚀 Features

- **AI-Powered Horoscopes**: Uses Google Gemini LLM for personalized insights
- **Vector Search**: ChromaDB for semantic horoscope retrieval
- **Multi-Language Support**: IndicTrans2 for translation to 12+ Indian languages
- **Caching**: Redis-based caching with configurable TTL
- **Containerized**: Full Docker setup with PostgreSQL, Redis, and ChromaDB
- **RESTful API**: FastAPI with automatic documentation

## 🏗️ Architecture

```
astrochat/
├── app/
│   ├── services/          # Service modules
│   │   ├── cache_service.py
│   │   ├── chroma_service.py
│   │   ├── gemini_service.py
│   │   ├── panchang_service.py
│   │   └── translation_service.py
│   ├── api.py            # FastAPI routes
│   ├── config.py         # Configuration
│   ├── database.py       # Database models
│   ├── models.py         # Pydantic models
│   ├── services.py       # Main business logic
│   ├── startup.py        # Application startup
│   └── utils.py          # Utility functions
├── tests/                # Test files
├── archive/              # Data files
├── docker-compose.yml    # Docker orchestration
├── Dockerfile           # Container definition
└── requirements.txt     # Python dependencies
```

## 🛠️ Quick Start

### Prerequisites
- Docker and Docker Compose
- Google Gemini API Key

### 1. Clone and Setup
```bash
git clone <repository-url>
cd astrochat
```

### 2. Start Services
```bash
./start.sh
```

The script will:
- Prompt for your Gemini API key
- Build and start all services
- Wait for services to be ready
- Display API endpoints

### 3. Test the API
```bash
curl -X POST "http://localhost:8000/horoscope" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Priya",
       "birth_date": "1995-08-20",
       "birth_time": "14:30",
       "birth_place": "Mumbai, India",
       "language": "hi"
     }'
```

## 📚 API Documentation

Once running, visit:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Supported Languages**: http://localhost:8000/languages

## 🌐 Supported Languages

- English (en)
- Hindi (hi)
- Bengali (bn)
- Tamil (ta)
- Telugu (te)
- Marathi (mr)
- Gujarati (gu)
- Kannada (kn)
- Malayalam (ml)
- Punjabi (pa)
- Odia (or)
- Assamese (as)

## 🔧 Configuration

Environment variables in `.env`:
```env
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=postgresql://astrochat:astrochat123@postgres:5432/astrochat
REDIS_URL=redis://redis:6379
CHROMA_PERSIST_DIRECTORY=/app/chroma_db
CACHE_TTL_MINUTES=30
DEBUG=True
LOG_LEVEL=INFO
```

## 🧪 Testing

Run tests:
```bash
cd tests
python test_setup.py
python test_translation.py
```

## 🐳 Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild
docker-compose build --no-cache
```

## 📊 Services

- **API**: FastAPI application (port 8000)
- **PostgreSQL**: Database (port 5432)
- **Redis**: Caching (port 6379)
- **ChromaDB**: Vector database (persistent)

## 🔍 Troubleshooting

### Model Loading Takes Time
The IndicTrans2 model (2.8GB) takes several minutes to load on first startup. This is normal.

### Cache Issues
Clear Redis cache:
```bash
docker-compose exec redis redis-cli FLUSHALL
```

### Database Issues
Reset database:
```bash
docker-compose down -v
docker-compose up -d
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request
