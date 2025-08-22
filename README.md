# 🌌 Astrochat - AI-Powered Multilingual Horoscope API

A modern horoscope API with AI-powered insights and neural machine translation for 12+ Indian languages.

## 🚀 Features

- **AI-Powered Horoscopes**: Google Gemini LLM for personalized insights
- **Neural Translation**: IndicTrans2 for 12+ Indian languages (Hindi, Bengali, Tamil, etc.)
- **Vector Search**: ChromaDB for semantic horoscope retrieval
- **Smart Caching**: Redis-based caching for performance
- **RESTful API**: FastAPI with automatic documentation

## 🌐 Translation Logic

1. **Generate**: AI creates personalized horoscope in English
2. **Translate**: IndicTrans2 neural model translates to target language
3. **Format**: Language-specific post-processing and cleanup
4. **Cache**: Store translated responses for performance

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
│   ├── horoscope_services.py  # Main business logic
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
- Python 3.8+
- Google Gemini API Key - shared in the email

### 1. Setup and Run
```bash
git clone https://github.com/kaushalkuma-r/astrochat.git
cd astrochat
./run.sh --- Will prompt you for the API key shared in the email
```

The `run.sh` script handles everything:
- Environment setup
- Dependency installation
- Service initialization
- API server startup

### 2. Test Translation API
```bash
# English (default)
curl -X POST "http://localhost:8000/horoscope" \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "birth_date": "1990-06-15", "language": "en"}'

# Hindi translation
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
The IndicTrans2 model takes several minutes to load on first startup. This is normal.

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
