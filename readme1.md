# 🎯 GNN-Based Personalized Post Recommendation API

This project is a FastAPI service that recommends personalized posts to users using a **Graph Neural Network (GNN)** model trained on user-post interactions.

---

## 📦 Features

- Personalized feed generation using a multi-relational GNN model.
- Rich post metadata including nested owner, category, and topic fields.
- Modular, readable, and extensible architecture.

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Tim-Alpha/video-recommendation-assignment.git
```

```bash
cd video-recommendation-engine
```

### 2. Create Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the API Server

    ```bash
    uvicorn app.app:app --reload
    ```

- The API will be available at: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- You can test endpoints at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Swagger UI)

---

## 📌 API Endpoint

### `GET /feed`

Returns personalized post recommendations.

#### 🔧 Query Parameters:

| Name           | Type   | Required | Description                                                  |
| -------------- | ------ | -------- | ------------------------------------------------------------ |
| `username`     | string | Required | Username of the user to personalize recommendations.         |
| `project_code` | int    | Optional | Filter recommendations to a specific category (if provided). |

#### 🧪 Example:

```bash
curl "http://127.0.0.1:8000/feed?username=afrobeezy"
```

---

## ✅ API Response Format

### When successful:

```json
{
  "status": "success",
  "post": [
    {
      "id": 101,
      "owner": {
        "first_name": "John",
        "last_name": "Doe",
        "name": "John Doe",
        "username": "johndoe",
        ...
      },
      "category": {
        "id": 7,
        "name": "DeFi",
        ...
      },
      "topic": {
        "id": 3,
        "name": "AI in Finance",
        ...
      },
      "title": "How DeFi is disrupting traditional banks",
      "tags": ["finance", "blockchain", "crypto"],
      "video_link": "https://youtube.com/xyz",
      ...
    }
  ]
}
```

---

## 🧠 How It Works

1. **User Identification**: Maps `username` to `user_id`.
2. **GNN Model**: Loads pretrained GNN (`multi_rel_gnn_model.pth`) and `graph_data.pt`.
3. **Embedding Inference**: Generates user-post similarity scores.
4. **Top-K Filtering**: Selects top posts the user hasn't interacted with.
5. **Post Formatting**: Formats post metadata into structured JSON.

---

## 🛠️ Development Notes

- GNN model: Implemented in `app/recommender.py`
- Helper modules:
  - `helper/interactions_data.py`: Data loading for interactions.
  - `helper/posts.py`: Post filtering/formatting logic.
  - `helper/users.py`: Username-to-ID mapping.
- Sample model training notebook: `helper/recommendation_model.ipynb`

---

## 📄 Requirements

Make sure the following Python packages are installed:

```
torch
pandas
fastapi
uvicorn
```

---

## 📤 Deployment

For production, remove `--reload` and serve with Gunicorn + Uvicorn workers:

```bash
gunicorn -k uvicorn.workers.UvicornWorker app.app:app
```

Consider using Docker and environment variables for configs.

---

## 🧾 License

MIT License. See `LICENSE` file for details.

---

## ✨ Acknowledgments

- Built using [FastAPI](https://fastapi.tiangolo.com/)
- GNN based on [PyTorch Geometric](https://pytorch-geometric.readthedocs.io/)
- Avatar generation via [UI Avatars](https://ui-avatars.com)

---

## 👨‍💻 Author

**Akshat** – [GitHub](https://github.com/your-username) • [LinkedIn](https://linkedin.com/in/your-profile)
