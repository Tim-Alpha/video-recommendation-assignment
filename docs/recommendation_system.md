# Technical Documentation: Video Recommendation System

This document provides a technical deep-dive into the architecture and logic of the Video Recommendation Engine.

## System Architecture

The application is built on a modern, decoupled, layered architecture:

1.  **Presentation Layer (Frontend):** A single-page application built with vanilla HTML, CSS, and JavaScript. It serves as the user interface and interacts with the backend via RESTful API calls. It is served directly by the FastAPI application.

2.  **API Layer (Backend - `app/api/`):** This is the main entry point for all client requests, built with FastAPI.
    -   **Endpoints (`app/api/endpoints/`):** Defines all API routes (`/feed`, `/feed/mood`, `/collect-data`). It handles HTTP request/response logic and data validation using Pydantic.
    -   **Dependencies (`app/api/deps.py`):** Manages dependencies, most notably the database session (`get_db`), which is injected into the endpoint functions.

3.  **Service Layer (Business Logic - `app/services/`):** This layer contains the core application logic, ensuring that the API layer remains thin and focused only on web concerns.
    -   **`recommendation_service.py`:** Implements the algorithms for generating video feeds. It contains separate logic for personalized "warm starts" and generic "cold starts" (including the new mood-based feature).
    -   **`data_collection_service.py`:** A dedicated service that acts as an ETL (Extract, Transform, Load) pipeline. It connects to the external Socialverse API, fetches raw data, and orchestrates the process of storing it in the local database using the CRUD layer.

4.  **Data Access Layer (CRUD - `app/crud/`):** This layer abstracts all direct database interactions.
    -   CRUD stands for Create, Read, Update, Delete.
    -   Each file (`crud_user.py`, `crud_post.py`) contains simple, reusable functions (e.g., `get_user_by_username`, `create_post`) that operate on a single database model. This prevents raw SQL or complex queries from cluttering the business logic.

5.  **Data Model Layer (Schema & DB - `app/models/`, `app/db/`):** This is the foundation of the data structure.
    -   **Models (`app/models/`):** Defines the database tables (`users`, `posts`, `interactions`) as Python classes using SQLAlchemy's ORM.
    -   **Database (`app/db/`):** Manages the database connection (`session.py`) and the declarative base (`base_class.py`) that all models inherit from.
    -   **Migrations (`alembic/`):** Alembic is used to manage and version the database schema. Any change to the SQLAlchemy models requires a new migration, ensuring the database schema always stays in sync with the code.

## Recommendation Logic Explained

The system employs two distinct strategies for providing recommendations.

### 1. Warm Start: Personalized Feed (`GET /feed?username={username}`)

This strategy is used when the user exists in our database and has a history of positive interactions (`like` or `inspire`).

1.  **User Identification:** The system fetches the user's record from the `users` table.
2.  **Interaction History:** It queries the `interactions` table to find all posts the user has previously interacted with. These are marked as "seen" and will be excluded from the final recommendation list to avoid repetition.
3.  **Preference Discovery:** The core of the personalization lies here. The system specifically queries for interactions of type `like` or `inspire`. It then joins this data with the `posts` table to identify the categories (`project_code`) that the user prefers.
4.  **Candidate Generation:** The system fetches a list of popular, unseen posts from these preferred categories.
5.  **Feed Augmentation:** If the number of candidates generated from preferred categories is not sufficient (e.g., less than 20), the feed is "topped up" with globally popular posts that the user has not yet seen. This ensures a full and engaging feed.

### 2. Cold Start: New Users & Mood-Based Feed

This strategy is used for users who are not in our database or have no interaction history.

#### a) Generic Cold Start (Fallback)
If a user is searched but has no "likes", the system falls back to a generic cold start:
1.  It calls the `get_popular_posts()` function.
2.  This function returns a list of the most recent posts from the `posts` table, providing a globally popular feed.

#### b) Interactive Cold Start (`GET /feed/mood?mood={mood}`)
This is a user-centric feature to solve the "new user" problem.
1.  The frontend presents the user with several mood options (e.g., "Inspired", "Motivated").
2.  When a mood is selected, the frontend calls the `/feed/mood` endpoint.
3.  The backend contains a predefined mapping (`MOOD_TO_CATEGORIES`) that links each mood to a list of relevant video categories.
4.  The `get_mood_based_feed` service function fetches popular videos from these mapped categories, shuffles them, and returns a curated feed. This provides instant, relevant content without requiring any user history.