# Video Recommendation Engine

A sophisticated recommendation system that suggests personalized video content based on user preferences and engagement patterns using deep neural networks. Reference: See motivational content recommendations in the [Empowerverse App ANDROID](https://play.google.com/store/apps/details?id=com.empowerverse.app) || [iOS](https://apps.apple.com/us/app/empowerverse/id6449552284).

## 🎯 Project Overview

This project implements a video recommendation system that:

* Delivers personalized content recommendations
* Handles cold start problems using mood-based recommendations
* Utilizes Graph/Deep neural networks for content analysis
* Integrates with external APIs for data collection
* Implements efficient data caching and pagination
* Handles edge cases and ensures proper error handling

## 🛠️ Technology Stack

* **Backend Framework**: FastAPI
* **Documentation**: Swagger/OpenAPI
* **Database**: MongoDB

## 📋 Prerequisites

* Python 3.8+
* Virtual environment (recommended)
* MongoDB server running locally or remotely

## 🚀 Getting Started

1. **Clone the Repository**

```bash
git clone https://github.com/Tim-Alpha/video-recommendation-assignment.git
cd video-recommendation-engine
```

2. **Set Up Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
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

6. **Start the Server**

```bash
uvicorn app.main:app --reload
```

## 📊 API Endpoints

### Recommendation Endpoints

1. **Get Personalized Feed**

```
GET /feed?username={username}
```

Returns personalized video recommendations for a specific user.

2. **Get Category-based Feed**

```
GET /feed?username={username}&project_code={project_code}
```

Returns category-specific video recommendations for a user.

### Data Collection Endpoints (Internal Use)

1. **Get All Viewed Posts**

```
GET https://api.socialverseapp.com/posts/view?page=1&page_size=1000&resonance_algorithm=<algorithm_token>
```

2. **Get All Liked Posts**

```
GET https://api.socialverseapp.com/posts/like?page=1&page_size=1000&resonance_algorithm=<algorithm_token>
```

3. **Get All Inspired Posts**

```
GET https://api.socialverseapp.com/posts/inspire?page=1&page_size=1000&resonance_algorithm=<algorithm_token>
```

4. **Get All Rated Posts**

```
GET https://api.socialverseapp.com/posts/rating?page=1&page_size=1000&resonance_algorithm=<algorithm_token>
```

5. **Get All Posts (Header required)**

```
GET https://api.socialverseapp.com/posts/summary/get?page=1&page_size=1000
```

6. **Get All Users (Header required)**

```
GET https://api.socialverseapp.com/users/get_all?page=1&page_size=1000
```

### Authorization

All external API calls require a header:

```json
"Flic-Token": "flic_11d3da28e403d182c36a3530453e290add87d0b4a40ee50f17611f180d47956f"
```