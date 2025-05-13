# Video Recommendation Engine

The **Video Recommendation Engine** is a system designed to provide personalized video recommendations to users based on a Graph Neural Network (GNN) model. It fetches data from the SocialVerse APIs, stores it in both SQLlite and Neo4j databases, and provides personalized video feeds using the HeteroGNN model.

## Features

* **Data Fetching & Database Integration**:

  * Fetches data from SocialVerse APIs and loads it into SQLlite and Neo4j databases.
  * Uses Alembic for database migrations.

* **Graph Neural Network**:

  * Implements a **HeteroGNN model** for personalized video recommendations.

* **API Endpoints**:

  * Provides APIs to fetch personalized feeds and posts, with attributes like category name and title.

* **Dynamic Configuration**:

  * Configurations like database URLs and authentication credentials are stored in environment files and can be easily modified.

## Folder Structure

```
video-recommendation-engine/
│
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── feed.py      # APIs to fetch personalized feed
│   │   │   └── data.py      # APIs to check health of the model and fetch updated records
│   │   └── main.py          # Entry point for the app
│   ├── core/
│   │   ├── config.py        # Configuration file for database URLs and auth creds
│   │   └── env.py           # Environment variables and settings
│   ├── models/
│   │   ├── database.py      # Queries Neo4j for posts and user attributes
│   │   └── recommendation.py # HeteroGNN model for video recommendations
│   ├── services/
│   │   ├── recommend_services.py  # Service layer to recommend posts and feeds
│   │   └── data_service.py       # Queries Neo4j for data fetching
│   └── __init__.py
├── database_fetching.py      # Fetches data from SocialVerse APIs and loads into SQLite and Neo4j
├── create_db.py              # Creates the initial SQLite database
└── requirements.txt          # Project dependencies
```

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/video-recommendation-engine.git
   cd video-recommendation-engine
   ```

2. **Install dependencies**:

   Use the `requirements.txt` file to install the necessary Python libraries.

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:

   Create a `.env` file and configure your database credentials and API settings. Example:

   ```
   DATABASE_URL=sqlite:///./db.sqlite3
   NEO4J_URL=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=yourpassword
   SOCIALVERSE_API_KEY=yourapikey
   ```

4. **Initialize the database**:

   Run Alembic to apply database migrations:

   ```bash
   alembic upgrade head
   ```

5. **Create the SQLite database**:

   If it's your first time running the application, create the SQLite database:

   ```bash
   python create_db.py
   ```

## Running the Application

1. **Start the application**:

   To start the app using `uvicorn`, run the following command:

   ```bash
   uvicorn app.main:app --reload
   ```

   This will run the application on `http://localhost:8000`.

2. **API Endpoints**:

   * `GET /feed?username={username}`: Fetch personalized feed for the given username.
   * `GET /feed?username={username}&project_code={project_code}`: Fetch personalized feed for the given username and project.
   * `GET /data`: Check the health of the model and get updated records.

## How It Works

1. **Data Fetching**:
   The `database_fetching.py` script fetches data from the **SocialVerse APIs** and stores it in both the **SQLite** and **Neo4j** databases.

2. **Database Queries**:

   * The `database.py` file in the `models` folder defines the queries to fetch posts and user attributes from the Neo4j database.

3. **Recommendation Model**:

   * The `recommendation.py` file contains the HeteroGNN model that generates personalized video recommendations for users.

4. **API Service**:

   * The `recommend_services.py` in the `services` folder provides the service to fetch and recommend posts and feeds.
   * The `data_service.py` file defines the queries for fetching data from the Neo4j database.

5. **Endpoints**:

   * The `feed.py` file defines two APIs to fetch personalized feeds based on a user's username and project code.

## Project Setup

* **Models**: HeteroGNN model for personalized recommendations and database queries.
* **Service Layer**: Fetches and recommends posts/feeds based on various attributes like category name, title, etc.
* **Endpoints**: API layer to interact with the front end for fetching and providing personalized feeds.

## Conclusion

This system leverages the power of **Graph Neural Networks** (GNN) to provide personalized video recommendations by efficiently querying data from both SQLlite and Neo4j databases. With an easy-to-use REST API, this system can be integrated with various applications to offer users personalized content feeds.
