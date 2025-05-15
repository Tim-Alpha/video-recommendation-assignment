
# 🚀 EmpowerVerse – Recommendation API

**EmpowerVerse** is an intelligent post recommendation system that delivers personalized content suggestions to users. It uses a **hybrid recommendation engine** powered by:

* 📊 **Collaborative Filtering** (based on user interactions)
* 🧠 **Content-Based Filtering** (based on post similarity using TF-IDF)


---

## 🧪 API Endpoints

| Route                    | Description                                           |
| ------------------------ | ----------------------------------------------------- |
| `GET /posts/view`        | Fetch all view interactions                           |
| `GET /posts/like`        | Fetch all post likes                                  |
| `GET /posts/inspire`     | Fetch all inspire interactions                        |
| `GET /posts/rating`      | Fetch post ratings with percentage                    |
| `GET /posts/summary/get` | Fetch post summaries and keywords                     |
| `GET /users/get_all`     | Fetch all registered users                            |
| `GET /feed?user_id=5`    | 🔥 Generate personalized recommendations for user `5` |

> ✅ `/feed` is the core ML-powered endpoint that triggers the **hybrid recommendation engine** to return top personalized post recommendations.

---

## 📬 Importing the Postman Collection

To test and explore the API routes easily using **Postman**, follow these steps:

1. Open **Postman**.
2. Click on **Import** (top left).
3. Choose **"File"** as the import method.
4. Locate and select the file:
   📄 `empowerverse.postman_collections.json`
5. Click **Import**.
6. You will now see a new folder named **EmpowerVerse** in your collection sidebar.

You can now test routes like:

* `GET /posts/view`
* `GET /feed?user_id=5`
* etc.

---


