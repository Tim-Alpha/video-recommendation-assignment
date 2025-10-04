# Video Recommendation Engine

A sophisticated, full-stack video recommendation system built with FastAPI and a vanilla JavaScript frontend. This engine delivers personalized video content based on user engagement patterns and solves the cold start problem with an interactive mood-based recommendation feature.

## 🌟 Features

-   **Personalized Feed:** Recommends videos based on a user's "like" and "inspire" history.
-   **Cold Start Solution:** New or inactive users receive recommendations based on globally popular content.
-   **Mood-Based Recommendations:** A unique feature allowing new users to get instant recommendations by selecting their current mood.
-   **Full-Stack Application:** A complete solution with a sleek, modern frontend and a powerful asynchronous backend.
-   **Robust Data Handling:** Utilizes a dedicated service to fetch, process, and store data from external APIs.
-   **Scalable Architecture:** Built with a clean, layered architecture (API -> Service -> CRUD -> Data).
-   **Professional Database Management:** Uses SQLAlchemy for ORM and Alembic for schema migrations.

## 🏛️ Project Architecture

The application follows a layered architecture to ensure a clear separation of concerns, making it highly maintainable and scalable.

```
+-------------------+      +----------------------+      +--------------------+      +-----------------+
|   Frontend        |----->|     API Layer        |----->|   Service Layer    |----->|   CRUD Layer    |----->+-----------+
| (HTML/CSS/JS)     |      |   (FastAPI)          |      | (Business Logic)   |      | (DB Operations) |      | Database  |
+-------------------+      | - Endpoints (feed.py)|      | - Recommendation   |      | - crud_user.py  |      | (SQLite)  |
                           | - Pydantic Schemas   |      | - Data Collection  |      | - crud_post.py  |      +-----------+
                           +----------------------+      +--------------------+      +-----------------+           ^
                                                                                                                   |
                                                                                                        +------------------+
                                                                                                        |   Data Layer     |
                                                                                                        | (SQLAlchemy Models)|
                                                                                                        +------------------+
```

1.  **Frontend (`frontend/index.html`):** A single-page application built with vanilla HTML, CSS, and JavaScript. It communicates with the backend API to fetch and display video recommendations.
2.  **API Layer (`app/api/`):** Handled by FastAPI. It defines the API routes (`/feed`, `/feed/mood`, `/collect-data`), validates request data, and structures the JSON responses.
3.  **Service Layer (`app/services/`):** Contains the core business logic.
    -   `RecommendationService`: Implements the algorithms for both personalized and mood-based recommendations.
    -   `DataCollectionService`: Manages the entire ETL (Extract, Transform, Load) process of fetching data from the external Socialverse API and storing it in the local database.
4.  **CRUD Layer (`app/crud/`):** Contains simple, reusable functions for direct database interaction (Create, Read, Update, Delete).
5.  **Data Layer (`app/models/`, `app/db/`):** Defines the database schema using SQLAlchemy models and manages the database session. Alembic controls the versioning of this layer.

## 🛠️ Technology Stack

-   **Backend Framework:** **FastAPI**
-   **Frontend:** **HTML5, CSS3, JavaScript (Vanilla)**
-   **Database:** **SQLite**
-   **ORM:** **SQLAlchemy**
-   **Database Migrations:** **Alembic**
-   **Data Validation:** **Pydantic**
-   **HTTP Client:** **HTTPX** (for asynchronous API calls)
-   **ASGI Server:** **Uvicorn**
-   **Environment Variables:** **python-dotenv**

## 🚀 Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites

-   Python 3.10+
-   A virtual environment tool (like `venv`)

### Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/video-recommendation-assignment.git
    cd video-recommendation-assignment
    ```

2.  **Set Up Virtual Environment**
    ```bash
    # Create the virtual environment
    python -m venv venv

    # Activate it
    # On Windows (PowerShell):
    .\venv\Scripts\Activate.ps1
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    Create a file named `.env` in the root project directory and add your API credentials.

    ```.env
    FLIC_TOKEN=your_valid_flic_token_here
    API_BASE_URL=https://api.socialverseapp.com
    DATABASE_URL=sqlite:///./database.db
    ```

5.  **Run Database Migrations (CRITICAL STEP)**
    This project uses Alembic to manage the database schema. These commands will create your `database.db` file and all the necessary tables (`users`, `posts`, `interactions`).

    ```bash
    # Step 1: Generate the migration script from your models
    alembic revision --autogenerate -m "Create initial tables"

    # Step 2: Apply the migration to the database
    alembic upgrade head
    ```

6.  **Start the Server**
    ```bash
    uvicorn app.main:app --reload
    ```
    The application will be running at `http://127.0.0.1:8000`.

## ⚙️ How to Use the Application

1.  **Start the Server:** Ensure the Uvicorn server is running.

2.  **Populate the Database:**
    -   Before you can get recommendations, you must fetch data from the external API.
    -   Use an API tool like Postman to send a **`POST`** request to the following endpoint:
        `http://127.0.0.1:8000/collect-data`
    -   Watch the terminal. The process will run in the background and will log its progress as it stores users, posts, and interactions.

3.  **Use the Frontend:**
    -   Open your web browser and navigate to `http://127.0.0.1:8000`.
    -   **For Cold Start / New Users:** Click on one of the mood buttons (e.g., "🚀 Motivated") to get an instant feed of relevant videos.
    -   **For Personalized Recommendations:**
        -   First, find a valid username by opening the `database.db` file with a tool like **DB Browser for SQLite** and looking in the `users` table.
        -   Enter that username into the search box on the webpage and click "Get Feed".
        -   You will receive a personalized list of recommendations.
    -   **Watch Videos:** Click on any video card to open the original video in a new tab.

## 📊 API Endpoints

The application exposes the following endpoints:

#### Frontend

-   **`GET /`**
    -   Serves the main `index.html` frontend application.

#### Recommendation API

-   **`GET /feed?username={username}`**
    -   Returns a personalized list of video recommendations for a given user.
-   **`GET /feed/mood?mood={mood}`**
    -   Returns a list of videos based on a selected mood (e.g., "Motivated", "Calm").

#### Data Management API (Internal Use)

-   **`POST /collect-data`**
    -   Triggers the background service to fetch all users, posts, and interactions from the external Socialverse API and store them in the local database.

You can view interactive documentation for all API endpoints by navigating to `/docs` on the running server (e.g., `http://127.0.0.1:8000/docs`).