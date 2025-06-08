# Video-Recommendation-System


A powerful backend system that delivers personalized and category-based motivational video recommendations using deep learning and hybrid recommendation models.

## 🚀 Project Features

* Personalized content recommendation based on user interactions.
* Handles cold-start problem using mood/category-based filtering.
* Hybrid approach using collaborative filtering + content-based embeddings.
* SBERT embeddings for user and post representation.
* Daily caching of embeddings and interaction data.
* Integrates with Empowerverse and Socialverse APIs.

## 🧰 Tech Stack

* **Backend**: FastAPI
* **ML**: SentenceTransformers (SBERT), FAISS, ALS (implicit)
* **Data**: Pandas, Scikit-learn
* **API Testing**: Postman

---

## 🧱️ System Architecture

* **User Embeddings**: Text features from bio, role, and user type encoded using SBERT; numerical features scaled with MinMaxScaler.
* **Post Embeddings**: Metadata (title, topic, slug, and post summary) embedded using SBERT.
* **Hybrid Model**:

  * **Collaborative Filtering**: Using Implicit ALS on user-post interactions.
  * **Content-Based Filtering**: Using SBERT and FAISS for semantic similarity.
  * **Blended Score**: Combines both methods with weighted fusion to rank posts.
* **Caching**:

  * Daily caching of embeddings and interactions in `cache/` using `pickle`.
  * Avoids recomputation unless the day changes.
* **Data Fetching**:

  * Fetches views, likes, inspires, ratings, users, and posts from the Socialverse API.
* **Serving Layer**:

  * FastAPI serves endpoints and resolves usernames to user\_ids.
  * Embeddings are used to generate feed responses in real time.

---

## 📁 Folder Structure

```
video-recommendation-engine/
├── app/
│   ├── routes/
│   │   └── feed.py           # FastAPI endpoint logic
│   └── main.py               # FastAPI entry point
├── model.py                  # Hybrid recommendation model + embedding logic
├── cache/                    # Stores pickled embeddings, DataFrames, and cache date
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not committed)
├── README.md
└── empowerverse_postman_collection.json   # Postman demo requests
```

---

## ⚙️ Setup Instructions

### 🔐 Prerequisites

* Python 3.8+
* Virtual environment (recommended)

### ✅ Installation

```bash
git clone https://github.com/Tim-Alpha/video-recommendation-assignment.git
cd video-recommendation-engine
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 🔐 Configure Environment Variables

Create a `.env` file in the root directory:

```
FLIC_TOKEN=your_flic_token
API_BASE_URL=https://api.socialverseapp.com
```

### ▶️ Run the Server

```bash
uvicorn app.main:app --reload
```

Then open: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📡 API Endpoints

### 🎯 Recommendation APIs

**Get Personalized Feed**
`GET /feed?username=<username>`

**Get Category-based Feed**
`GET /feed?username=<username>&project_code=<project_code>`

### 🔐 Authorization Header

All requests to Socialverse API use:

```
"Flic-Token": "your_flic_token"
```

---








