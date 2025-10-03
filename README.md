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

## 📋 Prerequisites

- Virtual environment (recommended)

## 🚀 Getting Started

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Tim-Alpha/video-recommendation-assignment.git
   ```
   ```bash
   cd video-recommendation-engine
   ```
1. **Set Up Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment Variables**
   Create a `.env` file in the root directory:

   ```env

   FLIC_TOKEN=your_flic_token
   API_BASE_URL=https://api.socialverseapp.com
   ```
4. **Run Database Migrations**

   ```bash
   alembic upgrade head
   ```
5. **Start the Server**

   ```bash
   uvicorn app.main:app --reload
   ```

## 📊 API Endpoints

### Recommendation Endpoints Has to Build

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

APIs for data collection:

### APIs

1. **Get All Viewed Posts** (METHOD: GET):

   ```
   https://api.socialverseapp.com/posts/view?page=1&page_size=1000&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if
   ```
2. **Get All Liked Posts** (METHOD: GET):

   ```
   https://api.socialverseapp.com/posts/like?page=1&page_size=1000&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if
   ```
3. **Get All Inspired posts** (METHOD: GET):

   ```
   https://api.socialverseapp.com/posts/inspire?page=1&page_size=1000&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if
   ```
4. **Get All Rated posts** (METHOD: GET):

   ```
   https://api.socialverseapp.com/posts/rating?page=1&page_size=1000&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if
   ```
5. **Get All Posts** (Header required*) (METHOD: GET):

   ```
   https://api.socialverseapp.com/posts/summary/get?page=1&page_size=1000
   ```
6. **Get All Users** (Header required*) (METHOD: GET):

   ```
   https://api.socialverseapp.com/users/get_all?page=1&page_size=1000
   ```

### Authorization

For autherization pass `Flic-Token` as header in the API request:

Header:

```json
"Flic-Token": "flic_e657dc77ce71262a4f5dc78e0c9e1bf02a7f0e186b664708c39369f182ad2518"
```

**Note**: All external API calls require the Flic-Token header:


## 📝 Submission Requirements

1. **GitHub Repository**
   - Submit a merge request from your fork or cloned repository.
   - Include a complete Postman collection demonstrating your API endpoints.
   - Add a docs folder explaining how your recommendation system works.
2. **Video Submission**
   - Introduction Video (30–40 seconds)
     - A short personal introduction (with face-cam).
   - Technical Demo (3–5 minutes)
     - Live demonstration of the APIs using Postman.
     - Brief overview of the project.
       Video Submission

3. **Notification**

   - Join the Telegram group: [Video Recommendation](https://t.me/+VljbLT8o75QxN2I9)
   - Notify upon completion

## ✅ Evaluation Checklist

- [ ] All APIs are functional
- [ ] Database migrations work correctly
- [ ] README is complete and clear
- [ ] Postman collection is included
- [ ] Videos are submitted
- [ ] Code is well-documented
- [ ] Implementation handles edge cases
- [ ] Proper error handling is implemented
