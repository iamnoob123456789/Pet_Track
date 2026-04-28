# Pet-Track Backend API

A comprehensive, production-ready backend for the Pet-Track application that uses AI-powered image similarity and hybrid matching to help reunite lost and found pets.

## Features

### Core Functionality
- **AI-Powered Image Similarity**: Uses CLIP model for advanced image embedding and similarity matching
- **Hybrid Matching System**: Combines image similarity with metadata (breed, color, size, age, location)
- **Location-Based Filtering**: Geospatial queries with radius-based search
- **Image Quality Check**: Automatic detection of blurry or low-quality images
- **Duplicate Detection**: Prevents duplicate pet listings using embedding similarity
- **Real-time Notifications**: Email and in-app notifications for matches and contact requests

### Authentication & Security
- **JWT-based Authentication**: Secure user authentication with MongoDB
- **Password Hashing**: Bcrypt-based password security
- **Privacy Protection**: Masked contact information until users accept connections
- **Rate Limiting**: API rate limiting to prevent abuse

### Data Management
- **MongoDB Integration**: Scalable NoSQL database with geospatial indexing
- **Comprehensive Data Models**: Rich pet, user, match, and notification schemas
- **Soft Deletes**: Data preservation with soft delete functionality
- **Audit Trails**: Complete tracking of user actions and system events

## Architecture

```
backend/
├── config/
│   └── database.py          # MongoDB configuration and connection
├── models/
│   ├── user.py             # User data models
│   ├── pet.py              # Pet data models
│   ├── match.py            # Match data models
│   ├── notification.py     # Notification data models
│   └── contact.py          # Contact data models
├── services/
│   ├── auth_service.py     # Authentication and JWT management
│   ├── image_similarity.py # Image processing and similarity
│   ├── hybrid_matching.py  # Hybrid matching algorithm
│   └── notification_service.py # Email and in-app notifications
├── routes/
│   ├── auth.py             # Authentication endpoints
│   ├── pets.py             # Pet management endpoints
│   ├── matches.py          # Match management endpoints
│   ├── contacts.py         # Contact management endpoints
│   └── notifications.py    # Notification endpoints
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
└── .env.example           # Environment configuration template
```

## Technology Stack

- **Framework**: FastAPI (Python 3.8+)
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: JWT with python-jose
- **Image Processing**: OpenCV, Pillow, sentence-transformers
- **ML Models**: CLIP (ViT-B-32) for image embeddings
- **Geospatial**: GeoPy for distance calculations
- **Notifications**: SMTP email + in-app notifications
- **Documentation**: Auto-generated OpenAPI/Swagger docs

## API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info
- `PUT /auth/me` - Update user profile
- `POST /auth/logout` - User logout

### Pets (`/pets`)
- `POST /pets/` - Create new pet listing
- `GET /pets/` - Get pets with filtering
- `GET /pets/{pet_id}` - Get specific pet
- `PUT /pets/{pet_id}` - Update pet listing
- `DELETE /pets/{pet_id}` - Soft delete pet
- `POST /pets/{pet_id}/matches` - Find matches for pet

### Matches (`/matches`)
- `GET /matches/` - Get user's matches
- `GET /matches/{match_id}` - Get specific match
- `POST /matches/{match_id}/review` - Accept/reject match
- `GET /matches/feed/lost-and-found` - Get lost & found feed
- `GET /matches/stats/overview` - Get match statistics

### Contacts (`/contacts`)
- `POST /contacts/` - Initiate contact request
- `GET /contacts/` - Get user's contacts
- `GET /contacts/{contact_id}` - Get specific contact
- `POST /contacts/{contact_id}/respond` - Respond to contact
- `POST /contacts/{contact_id}/reveal-contact` - Reveal contact info

### Notifications (`/notifications`)
- `GET /notifications/` - Get user notifications
- `GET /notifications/unread-count` - Get unread count
- `POST /notifications/{notification_id}/mark-read` - Mark as read
- `POST /notifications/mark-all-read` - Mark all as read
- `DELETE /notifications/{notification_id}` - Delete notification

## Installation & Setup

### Prerequisites
- Python 3.8+
- MongoDB 4.4+
- Redis (optional, for caching)

### Setup Steps

1. **Clone and navigate to backend**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Start MongoDB**:
```bash
# On macOS with Homebrew
brew services start mongodb-community

# On Ubuntu
sudo systemctl start mongod

# On Windows
net start MongoDB
```

6. **Run the application**:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Setup (Alternative)

```bash
# Build image
docker build -t pet-track-backend .

# Run with MongoDB
docker-compose up
```

## Configuration

### Environment Variables

Key environment variables in `.env`:

- `MONGODB_URL`: MongoDB connection string
- `SECRET_KEY`: JWT secret key (change in production!)
- `EMAIL_USERNAME/EMAIL_PASSWORD`: SMTP credentials
- `APP_URL`: Frontend application URL

### Database Indexes

The application automatically creates optimal indexes on startup:
- Users: email, username (unique)
- Pets: owner_id, status, breed, color, location (2dsphere)
- Matches: lost_pet_id, found_pet_id, match_score
- Notifications: user_id, created_at

## Matching Algorithm

### Hybrid Scoring System

The matching system uses a weighted combination:

```
Hybrid Score = (Image Similarity × 0.6) + 
              (Metadata Similarity × 0.25) + 
              (Location Similarity × 0.15)
```

### Image Similarity
- Uses CLIP ViT-B-32 model for image embeddings
- Cosine similarity between embeddings
- Automatic image quality assessment
- Duplicate detection with 95% similarity threshold

### Metadata Similarity
- **Breed Matching**: Exact match + breed variations (40% weight)
- **Color Matching**: Overlapping color sets (30% weight)
- **Size Matching**: Categorical similarity (20% weight)
- **Age Matching**: Categorical similarity (10% weight)

### Location Similarity
- Haversine distance calculation
- Exponential decay based on distance
- Configurable maximum distance (default: 50km)

## Performance Optimizations

### Database
- Geospatial indexing for location queries
- Compound indexes for common query patterns
- Pagination for large result sets
- Connection pooling with Motor

### ML Models
- Model caching in memory
- Batch processing for multiple images
- Async image processing
- Quality filtering before processing

### API
- Response caching for static data
- Rate limiting for abuse prevention
- Async request handling
- Optimized query patterns

## Security Features

### Authentication
- JWT tokens with expiration
- Secure password hashing with Bcrypt
- Token refresh mechanism
- Session management

### Data Privacy
- Masked contact information
- Privacy controls for user data
- GDPR-compliant data handling
- Audit logging for sensitive operations

### API Security
- CORS configuration
- Rate limiting
- Input validation with Pydantic
- SQL injection prevention (MongoDB)

## Monitoring & Logging

### Logging
- Structured logging with Python logging
- Different log levels (DEBUG, INFO, WARNING, ERROR)
- File and console output
- Request/response logging

### Health Checks
- `/health` endpoint for monitoring
- Database connection status
- ML model loading status
- Service availability checks

## Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

### Test Coverage
- Unit tests for services
- Integration tests for API endpoints
- Database operation tests
- Authentication flow tests

## Deployment

### Production Considerations
- Use HTTPS with SSL certificates
- Configure proper CORS for production domains
- Set up monitoring and alerting
- Implement backup strategy for MongoDB
- Use environment-specific configuration

### Environment Variables for Production
- Strong, randomly generated `SECRET_KEY`
- Production MongoDB connection string
- SMTP credentials for transactional email
- Redis configuration for caching
- Logging configuration for production

## API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## Trade-offs & Limitations

### Current Limitations
- **Model Size**: CLIP model requires ~500MB memory
- **Processing Time**: Image embedding takes 1-3 seconds per image
- **Scalability**: Single-server deployment (can be scaled with load balancers)
- **Real-time Updates**: No WebSocket support (can be added)

### Design Trade-offs
- **MongoDB vs PostgreSQL**: Chose MongoDB for flexible schema and geospatial features
- **CLIP vs Custom Models**: CLIP provides good generalization but custom models could be more accurate
- **Sync vs Async**: Async for better concurrency, but requires careful error handling

### Future Improvements
- **Vector Database**: Add FAISS or Pinecone for faster similarity search
- **Model Optimization**: Quantize models for faster inference
- **Caching Layer**: Redis for frequently accessed data
- **Background Jobs**: Celery for async processing
- **WebSocket Support**: Real-time notifications
- **Microservices**: Split into separate services for better scalability

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
