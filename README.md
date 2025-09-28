# 🎬 Socialverse Video Recommender

An AI-powered video recommendation system built with **FastAPI**, **Streamlit**, and **SQLite**.  
It uses **TF-IDF**, **KMeans clustering**, and **cosine similarity** to recommend personalized video content to users based on their past interactions and chosen categories.

---

##  Project Structure

video-recommendation-assignment/
│── app/
│ ├── data.py # Database connection & session setup
│ ├── models/
│ │ └── model.py # SQLAlchemy ORM models (User, Post, Interaction)
│ ├── recommender.py # Core recommendation engine
│ └── main.py # FastAPI backend (API endpoint: /feed)
│── migrations/ # Alembic migrations for DB schema
│── streamlit_app.py # Streamlit frontend (UI for users)
│── app.db # SQLite database
│── requirements.txt # Python dependencies
│── README.md # Project documentation
│── .gitignore # Ignored files (venv, db, cache, etc.)


---

## Technologies Used

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/)
- **Frontend:** [Streamlit](https://streamlit.io/)
- **Database:** SQLite + SQLAlchemy ORM
- **Migrations:** Alembic
- **Machine Learning:** 
  - TF-IDF Vectorizer (text feature extraction)
  - KMeans clustering (grouping posts)
  - Cosine similarity (user–post matching)

---

##  Getting Started

###  Clone the repository
```bash
git clone https://github.com/your-username/video-recommendation-assignment.git
cd video-recommendation-assignment
2. Create a virtual environment
bash
Copy code
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
3 .Install dependencies
bash
Copy code
pip install -r requirements.txt
4️. Setup the database
Initialize Alembic migrations and create tables:

bash
Copy code
alembic upgrade head
(Or if DB already exists, skip this step)

5Run the FastAPI backend
bash
Copy code
uvicorn app.main:app --reload --port 8000
Backend runs at  http://127.0.0.1:8000/feed

 Run the Streamlit frontend
bash
Copy code
streamlit run streamlit_app.py
Frontend runs at  http://localhost:8501

API Testing with Postman
Example request:

nginx
Copy code
GET http://127.0.0.1:8000/feed?username=Anushka&project_code=Education
Response:

json
Copy code
{
  "username": "Anushka",
  "recommendations": [
    {
      "post_id": "5175",
      "title": "Great things never come from comfort zones",
      "category": "Motivation",
      "mood": "Inspiring"
    }
  ]
}
Streamlit UI
Enter a username

Choose a category from dropdown

Get personalized recommendations with titles, categories, and moods

