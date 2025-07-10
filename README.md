# Video Recommendation Engine

A sophisticated recommendation system that suggests personalized video content based on user preferences and engagement patterns using deep neural networks. Ref: to see what kind of motivational content you have to recommend, take reference from our Empowerverse App [ANDROID](https://play.google.com/store/apps/details?id=com.empowerverse.app) || [iOS](https://apps.apple.com/us/app/empowerverse/id6449552284).

## 🎯 Project Overview

This project implements a video recommendation algorithm that:

- Delivers personalized content recommendations
- Handles cold start problems using mood-based recommendations
- Utilizes Graph/Deep neural networks for content analysis
- Integrates with external APIs for data collection
- Implements efficient data caching and pagination

## 🛠️ Technology Stack

- **Backend Framework**: FastAPI
- **Documentation**: Swagger/OpenAPI
- **ORM**: SQLAlchemy
- **ML/AI**: PyTorch, scikit-learn, pandas, numpy
- **Graph Neural Networks (GNN)**: Custom GNN model using PyTorch (see `app/ml/gnn_model.py`)
- **Graph Processing**: NetworkX
- **Database**: SQLite (default, can be changed)
- **Async HTTP Client**: httpx
- **Environment Management**: python-dotenv
- **Testing**: pytest

## 📋 Prerequisites

- Python 3.8+
- Virtual environment (recommended)

## 🚀 Getting Started

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Tim-Alpha/video-recommendation-assignment.git
   cd video-recommendation-engine
   ```
2. **Set Up Virtual Environment**

   ```bash
   python -m venv venv
   # On Unix/Mac
   source venv/bin/activate
   # On Windows
   venv\Scripts\activate
   ```
3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Environment Variables**
   Create a `.env` file in the root directory:

   ```env
   FLIC_TOKEN=your_flic_token
   API_BASE_URL=https://api.socialverseapp.com
   ```
5. **Run Database Migrations**

   ```bash
   alembic upgrade head
   ```
6. **Seed the Database with Example Data**

   This will populate your database with diverse example users, categories, topics, posts, and interactions:

   ```bash
   python -m app.seed_data
   ```

7. **Start the Server**

   ```bash
   uvicorn app.main:app --reload
   ```

8. **Access API Documentation**

   Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser for interactive Swagger UI.

## 📊 API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /feed?username={username}&limit={n}` - Personalized feed
- `GET /feed?username={username}&project_code={project_code}` - Category-based feed
- `POST /sync` - Sync data from external API
- `GET /stats` - System statistics
- `GET /users` - List users
- `GET /posts` - List posts (with filters)
- `GET /categories` - List categories
- `GET /topics` - List topics (with filters)

## 🧪 Running Tests

Run the included tests with:

```bash
pytest
```

## 🐞 Error Handling

- All endpoints return clear error messages and HTTP status codes.
- Errors are logged using Python's `logging` module.
- See code for details on exception handling in each service and endpoint.

## 📝 Requirements

All dependencies are listed in `requirements.txt`. Make sure to install them before running the app.

## 📂 Project Structure

- `app/` - Main application code
- `app/ml/` - ML models (GNN, embeddings, see `gnn_model.py` for the GNN implementation)
- `app/recommendation_engine.py` - Recommendation engine using GNN and other ML techniques
- `app/services.py` - Data and recommendation services
- `app/external_api.py` - External API integration
- `app/seed_data.py` - Script to seed the database with example data
- `tests/` - Test cases
- `alembic/` - Database migrations

## 📦 Submission Requirements

- Complete GitHub repository
- Postman collection (`video-recommendation-api.postman_collection.json`)
- Documentation in `docs/`
- Video demo (see original instructions)

## ✅ Evaluation Checklist

- [x] All APIs are functional
- [x] Database migrations work correctly
- [x] README is complete and clear
- [x] Postman collection is included
- [x] Code is well-documented
- [x] Implementation handles edge cases
- [x] Proper error handling is implemented
- [x] Diverse example data is seeded

---

For any issues, please check the logs or open an issue on GitHub.
