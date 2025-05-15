
# `recommendation_engine.py` – Recommendation Engine

This module implements a hybrid **RecommendationEngine** that generates personalized post suggestions using both **collaborative filtering** (based on user interactions) and **content-based filtering** (based on post text similarity).

---

##  Core Responsibilities

* Generate a **user-post interaction matrix**.
* Compute **content similarity** using TF-IDF.
* Calculate **user-user similarity** for collaborative filtering.
* Recommend posts by combining collaborative and content-based scores, with category-based boosting.

---

## 1. 🧱 Creating the Interaction Matrix

### 📌 Method: `build_interaction_matrix()`

A user-post matrix is constructed where:

* **Rows** = Users
* **Columns** = Posts
* **Values** = Weighted sum of interactions (likes, views, inspires, ratings)

### 📥 Data Sources (via `database_manager.py`):

* `fetch_post_likes_ids()` → Likes data
* `fetch_post_views_ids()` → Views data
* `fetch_post_inspires_ids()` → Inspires data
* `fetch_post_ratings_ids_and_rating()` → Ratings data
* `load_updated_post_summaries()` → Posts metadata (summary, keywords)

### 🔢 Weighting Interactions:

| Interaction  | Weight       |
| ------------ | ------------ |
| Like         | 1.0          |
| View         | 0.5          |
| Inspire      | 1.5          |
| Rating > 50% | rating/100.0 |

> Multiple interactions are **accumulated**, e.g., a like + view = 1.5

### 🧮 Output Example:

```
         | post_1 | post_2 | post_3
-------------------------------------
user_1   |  1.5   |  0.0   |  0.75
user_2   |  0.0   |  2.0   |  0.0
```

---

## 2. 🧾 TF-IDF Content Similarity

### 📌 Method: `compute_content_similarity()`

Calculates post-to-post similarity using textual data.

###  Data Preparation:

* `summary` and `keywords` fields are merged to form `text_content`.
* `keywords` list is flattened to space-separated strings.

Example:

```
summary = "This is about AI innovation"
keywords = ["tech", "AI"]
text_content = "This is about AI innovation tech AI"
```

### 🔧 TF-IDF Vectorizer:

* `stop_words="english"`: Ignores common words
* `max_features=5000`: Limits vocabulary to reduce memory

### 📈 Cosine Similarity Matrix:

```
         | post_1 | post_2 | post_3
-------------------------------------
post_1   |  1.0   |  0.8   |  0.2
post_2   |  0.8   |  1.0   |  0.3
post_3   |  0.2   |  0.3   |  1.0
```

---

## 3. 🎯 Generating Recommendations

### 📌 Method: `recommend_posts(user_id, category=None, num_recommendations=10)`

Combines collaborative and content filtering for post recommendation.

---

###  Collaborative Filtering

#### Step 1: Compute User Similarity

* `compute_user_similarity()`: Cosine similarity between rows of interaction matrix
* Measures how similarly two users interact with posts

#### Step 2: Collaborative Scoring

```python
collab_scores += interaction_matrix.loc[sim_user] * similarity
```

* Adds weighted scores from top 10 similar users

---

###  Content-Based Filtering

* For each post the user interacted with, sum its similarity with other posts:

```python
content_scores += content_similarity_df.loc[post_id]
```

---

###  Combining Scores

```python
final_scores = 0.6 * collab_scores + 0.4 * content_scores
```

####  Category Boosting

* Identify top 3 categories from user's interactions
* Boost relevant posts: `score *= 1.2`

####  Filtering

* Exclude previously interacted posts
* If a category is specified, filter by that category

---

### ✅ Output

Returns `num_recommendations` post\_ids with the highest scores.

---

## ✅ Example Flow

```text
User calls /feed?user_id=123

 ↓ Calls → predict.py → recommendation_engine.py

     ↓ Builds interaction matrix
     ↓ Computes content similarity
     ↓ Computes user similarity
     ↓ Scores posts (collab + content + category boost)
     ↓ Filters and returns top N posts
```

---


