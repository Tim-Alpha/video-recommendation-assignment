# 🗂️ `database_manager.py` – EmpowerVerse Data Pipeline

The `database_manager.py` module is responsible for **initializing**, **fetching**, and **storing** all the user-post interaction data required by the EmpowerVerse recommendation engine.

It acts as the **backbone data layer** of the system, building and maintaining the SQLite database (`data.db`) that feeds into the ML model.

---

## ⚙️ Responsibilities

### 🔹 1. **Fetch-and-Store Functions**

* Functions like `fetch_and_store_users()`, `fetch_and_store_post_views()`, etc.:

  * **Fetch** data from the EmpowerVerse API (`http://localhost:8000/...`).
  * **Store** the data into local SQLite tables using SQLAlchemy models (`User`, `Post`, `PostView`, etc.).
* These functions populate the database when it's empty or newly created.

### 🔹 2. **Fetch Functions**

* Functions like `fetch_post_likes_ids()`, `fetch_post_views_ids()`, etc.:

  * Query the database for **lightweight subsets** of data like user-post ID pairs.
  * Return dictionaries such as:

    ```python
    {
      "likes": [{"user_id": 1, "post_id": 12}, ...]
    }
    ```
  * Ideal for **analytics**, **API responses**, or **quick lookups**.

### 🔹 3. **Load Functions**

* Functions like `load_post_ratings()`, `load_post_views()`, etc.:

  * Return **full records** from tables like `PostRating`, `PostInspire`, etc.
  * Format:

    ```python
    {
      "ratings": [{"id": 1, "user_id": 2, "post_id": 3, "rating": 4.5}, ...]
    }
    ```
  * Useful for **detailed data views**, **admin dashboards**, or **data analysis**.

---


## 🚨 Execution Order

Before using the `/feed` route or running any recommendation logic:

### ✅ **Run this file once to create and populate the database**:

```bash
python database_manager.py
```

This will:

* Call `create_db()` internally
* Check if `data.db` exists or is empty
* Fetch all API data (users, posts, views, likes, etc.)
* Store it in `data.db`

---

## 🧠 Used By: `recommendation_engine.py`

The recommendation engine imports `database_manager.py` to:

* Access `fetch_*()` functions for interaction matrices
* Use `load_*()` functions for detailed analysis
* Provide data to the ML logic inside `/feed?user_id=X`

---

## 📁 Tables Created

* `User`
* `Post`
* `PostView`
* `PostLike`
* `PostInspire`
* `PostRating`
* `PostSummary`




