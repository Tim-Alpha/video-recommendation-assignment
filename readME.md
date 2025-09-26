# Video Recommendation API

A simple FastAPI-based video recommendation system.  
This project demonstrates basic recommendation logic (cold start, category-based, user history) with endpoints to fetch recommended videos or filter by category.

---

## 📂 Project Structure

```
.
├── video-recommender/         # Main application module
│   ├── __init__.py
│   ├── api.py                 # Defines FastAPI routes / logic
│   └── data.py                # Sample video & user data, mood‑to‑category map
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation (this file)
└── venv/                      # (Optional) Virtual environment folder
```

---
## Data used and model work
Due to error while using using from given API's , custom data has been used that classifies data into 3 different categories
out model can recommend that data


## Deep learning model
Here i made 2 tower NN model, one processing user data and other processing video data taking their dot product should give us the probability of user to like a particular video
Due to time contrainst and some issue faces, i could only run the data on random dummty data
## 📡 API Endpoints

### `GET /feed`

Retrieve a personalized feed for a user.

**Query Parameters:**

- `username`
- `category`
