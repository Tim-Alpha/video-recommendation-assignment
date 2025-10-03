
# API Routes Documentation

This document provides an overview of the API endpoints defined in the `routes.py` module. These routes are designed using FastAPI and interact with an external API service using authentication tokens and structured response models.

---

## 🔧 Setup

* **Technologies Used**:

  * [FastAPI] – for route creation and API handling
  * [Pydantic] – for data validation and response schemas
  * `requests` – for external API communication
  * `dotenv` – for securely loading environment variables

* **Environment Variables**:

  * `FLIC_TOKEN`: Authentication token for secured routes
  * `API_BASE_URL`: Base URL of the external API
  * `RESONANCE_ALGORITHM`: used to configure the external API's recommendation logic
  * `PAGE_SIZE`: Number of items fetched per page
---

## 📌 Endpoints

### 1. `/posts/view`

**Method**: `GET`
**Description**: Fetches all viewed posts with pagination.

* **Returns**:

  ```json
  {
    "posts": [...],
    "pages": <int>
  }
  ```

---

### 2. `/posts/like`

**Method**: `GET`
**Description**: Retrieves posts the user has liked.

* **Returns**:

  ```json
  {
    "posts": [...],
    "pages": <int>
  }
  ```

---

### 3. `/posts/inspire`

**Method**: `GET`
**Description**: Retrieves posts the user found inspiring.

* **Returns**:

  ```json
  {
    "posts": [...],
    "pages": <int>
  }
  ```

---

### 4. `/posts/rating`

**Method**: `GET`
**Description**: Retrieves posts rated by the user.

* **Returns**:

  ```json
  {
    "posts": [...],
    "pages": <int>
  }
  ```

---

### 5. `/posts/summary/get`

**Method**: `GET`
**Description**: Fetches all post summaries using the `FLIC_TOKEN` for authentication.

* **Returns**:

  ```json
  {
    "posts": [...],
    "pages": <int>
  }
  ```

---

### 6. `/users/get_all`

**Method**: `GET`
**Description**: Fetches all registered users using the `FLIC_TOKEN`.

* **Returns**:

  ```json
  {
    "users": [...],
    "pages": <int>
  }
  ```

---

### 7. `/feed`

**Method**: `GET`
**Description**: Generates a list of recommended post IDs for a user. Optionally filtered by category.

* **Query Parameters**:

  * `user_id` (required)
  * `category` (optional)

* **Internal Flow**:

  * Calls `predict_posts(user_id, category)`
  * Internally uses:

    * `predict.py` → `recommendation_engine.py` → `database_manager.py`
  * Returns predicted post IDs.

* **Returns**:

  ```json
  {
    "recommended_posts": [<post_id_1>, <post_id_2>, ...]
  }
  ```

---

## 🧪 Response Models

Each route returns structured responses using Pydantic models like `PostResponse`, `UserResponse`, and `FeedResponse` to ensure consistency.

---

