# Pet-Track: AI-Powered Pet Identification & Matching System

A comprehensive, production-ready mobile application that uses advanced AI and computer vision to help reunite lost pets with their families through intelligent image similarity matching and hybrid algorithms.

## 🌟 Features

### Core Functionality
- **🤖 AI-Powered Image Similarity**: Uses CLIP ViT-B-32 model for advanced image embeddings and similarity matching
- **🎯 Hybrid Matching System**: Combines image similarity (60%) + metadata (25%) + location (15%) for accurate results
- **📍 Location-Based Filtering**: Geospatial queries with radius-based search (5km, 10km, etc.)
- **🔍 Image Quality Check**: Automatic detection of blurry or low-quality images with user feedback
- **🚫 Duplicate Detection**: Prevents duplicate pet listings using 95% embedding similarity threshold
- **🔔 Real-Time Notifications**: Email and in-app notifications for matches and contact requests

### User Experience
- **📱 Clean Mobile UI**: Modern, intuitive Flutter interface with Material Design
- **📸 Easy Image Upload**: Camera integration with quality validation
- **🎛️ Smart Filtering**: Filter by breed, color, location, date, and status
- **💬 Safe Contact System**: Masked contact information until users accept connections
- **📊 Match Analytics**: Detailed match statistics and confidence scores

### Technical Features
- **🔐 JWT Authentication**: Secure user authentication with MongoDB
- **🗄️ Scalable Database**: MongoDB with geospatial indexing
- **⚡ FastAPI Backend**: High-performance async Python backend
- **🎯 Top-K Matching**: Returns top 5 best matches with confidence scores
- **🔄 Real-time Updates**: Live matching when new pets are added

## 🏗️ Architecture

### Backend (Python/FastAPI)
```
backend/
├── config/
│   └── database.py          # MongoDB configuration & indexes
├── models/
│   ├── user.py             # User data models
│   ├── pet.py              # Pet data models
│   ├── match.py            # Match data models
│   ├── notification.py     # Notification models
│   └── contact.py          # Contact models
├── services/
│   ├── auth_service.py     # JWT authentication
│   ├── image_similarity.py # CLIP model & image processing
│   ├── hybrid_matching.py  # Hybrid matching algorithm
│   └── notification_service.py # Email & notifications
├── routes/
│   ├── auth.py             # Authentication endpoints
│   ├── pets.py             # Pet management
│   ├── matches.py          # Match management
│   ├── contacts.py         # Contact system
│   └── notifications.py    # Notification system
└── main.py                 # FastAPI application
```

### Frontend (Flutter)
```
lib/
├── models/
│   ├── user.dart           # User models
│   ├── pet.dart            # Pet models
│   └── match.dart          # Match models
├── services/
│   └── api_service.dart    # API client
├── screens/
│   ├── auth/              # Authentication screens
│   ├── home/              # Home & feed
│   ├── pet/               # Pet management
│   ├── matches/           # Match results
│   └── profile/           # User profile
├── widgets/              # Reusable components
└── config.dart           # App configuration
```

## 🚀 Quick Start

### Prerequisites
- **Backend**: Python 3.8+, MongoDB 4.4+, Redis (optional)
- **Frontend**: Flutter 3.0+, Dart 3.0+
- **Development**: Android Studio / VS Code

### Backend Setup

1. **Navigate to backend directory**:
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

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your MongoDB URL, JWT secret, and email settings
```

5. **Start MongoDB**:
```bash
# macOS
brew services start mongodb-community

# Ubuntu
sudo systemctl start mongod

# Windows
net start MongoDB
```

6. **Run the backend**:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Navigate to root directory**:
```bash
cd pet_track
```

2. **Install Flutter dependencies**:
```bash
flutter pub get
```

3. **Update configuration**:
```bash
# Edit lib/config.dart with your backend URL
# Replace with lib/config_updated.dart
```

4. **Run the app**:
```bash
flutter run
```

## 📱 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user
- `PUT /auth/me` - Update profile
- `POST /auth/logout` - Logout

### Pets
- `POST /pets/` - Create pet listing
- `GET /pets/` - Get pets with filtering
- `GET /pets/{id}` - Get specific pet
- `PUT /pets/{id}` - Update pet
- `DELETE /pets/{id}` - Delete pet
- `POST /pets/{id}/matches` - Find matches

### Matches
- `GET /matches/` - Get user's matches
- `GET /matches/{id}` - Get specific match
- `POST /matches/{id}/review` - Accept/reject match
- `GET /matches/feed/lost-and-found` - Public feed
- `GET /matches/stats/overview` - User statistics

### Contacts
- `POST /contacts/` - Initiate contact
- `GET /contacts/` - Get user's contacts
- `POST /contacts/{id}/respond` - Respond to contact
- `POST /contacts/{id}/reveal-contact` - Reveal full contact info

## 🧠 Matching Algorithm

### Hybrid Scoring System
```
Hybrid Score = (Image Similarity × 0.6) + 
              (Metadata Similarity × 0.25) + 
              (Location Similarity × 0.15)
```

### Image Similarity
- **Model**: CLIP ViT-B-32 (512-dimensional embeddings)
- **Similarity**: Cosine similarity between embeddings
- **Quality Check**: Resolution, blur, brightness validation
- **Duplicate Detection**: 95% similarity threshold

### Metadata Matching
- **Breed**: Exact match + common variations (40% weight)
- **Color**: Overlapping color sets (30% weight)
- **Size**: Categorical similarity (20% weight)
- **Age**: Categorical similarity (10% weight)

### Location Similarity
- **Distance**: Haversine formula for great-circle distance
- **Scoring**: Exponential decay based on distance
- **Default**: 50km maximum radius

## 🔧 Configuration

### Environment Variables (Backend)
```bash
# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=pet_track

# Authentication
SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# Application
APP_URL=http://localhost:3000
API_URL=http://localhost:8000
```

### Flutter Configuration
```dart
class Config {
  static String get apiBaseUrl => 'http://localhost:8000';
  static const int defaultPageSize = 20;
  static const double defaultMatchThreshold = 0.6;
  static const int defaultTopKMatches = 5;
}
```

## 📊 Performance & Scalability

### Database Optimization
- **Indexes**: Geospatial, compound, and text indexes
- **Pagination**: Cursor-based pagination for large datasets
- **Caching**: Redis integration for frequently accessed data

### API Performance
- **Async Processing**: FastAPI with async/await
- **Connection Pooling**: Motor async MongoDB driver
- **Rate Limiting**: Prevent API abuse
- **Compression**: Gzip response compression

### ML Model Optimization
- **Model Caching**: In-memory model storage
- **Batch Processing**: Multiple images processed together
- **Quality Filtering**: Reject poor quality images early

## 🔒 Security Features

### Authentication
- **JWT Tokens**: Secure, expiring access tokens
- **Password Hashing**: Bcrypt with salt
- **Token Refresh**: Automatic token renewal
- **Session Management**: Secure logout

### Data Privacy
- **Contact Masking**: Partial email/phone until acceptance
- **Privacy Controls**: User-controlled data sharing
- **GDPR Compliance**: Data deletion and export
- **Audit Logging**: Track all sensitive operations

### API Security
- **CORS**: Configurable cross-origin requests
- **Input Validation**: Pydantic model validation
- **SQL Injection Prevention**: Parameterized queries
- **HTTPS Ready**: SSL/TLS support

## 🌍 Trade-offs & Limitations

### Current Limitations
- **Model Size**: CLIP model requires ~500MB RAM
- **Processing Time**: 1-3 seconds per image for embedding
- **Scalability**: Single-server deployment (can be scaled)
- **Offline Support**: Limited offline functionality

### Design Decisions
- **MongoDB vs PostgreSQL**: Chose MongoDB for flexible schema and geospatial features
- **CLIP vs Custom Models**: CLIP provides better generalization
- **JWT vs Sessions**: JWT for better scalability and mobile support
- **REST vs GraphQL**: REST for simplicity and caching

### Future Improvements
- **Vector Database**: FAISS or Pinecone for faster similarity search
- **Model Optimization**: Quantization and pruning for faster inference
- **Microservices**: Split into separate services for better scaling
- **WebSocket Support**: Real-time notifications and live updates
- **Offline Mode**: Caching and sync for offline functionality

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### Development Guidelines
- Follow Dart/Flutter style guidelines
- Write tests for new features
- Update documentation
- Keep commits small and focused

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CLIP Model**: OpenAI for the powerful image-text model
- **FastAPI**: For the amazing async web framework
- **Flutter**: For the beautiful cross-platform UI framework
- **MongoDB**: For the flexible and scalable database

## 📞 Support

- **Documentation**: Check the `/docs` endpoint when backend is running
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact the development team

---

**Built with ❤️ for pet lovers everywhere**
