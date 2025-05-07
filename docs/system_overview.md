# How the Video Recommendation System Works

## 1. Graph-based Recommendation

The recommendation engine uses a GNN (Graph Neural Network) model trained on a bipartite graph of user-post interactions.

- **Nodes**: Users and posts
- **Edges**: Interactions such as views or likes
- **Goal**: Recommend unseen posts to users based on learned embeddings.

## 2. Model Details

- Model: Multi-relational GNN
- Framework: PyTorch Geometric
- Input: user_id, post_id mappings, graph structure
- Output: Top-k personalized post IDs

## 3. Inference Flow

- If `username` is present in user mapping:
  - Embed user and all posts
  - Score unseen posts
  - Filter by `category_id` if provided
- Otherwise:
  - Random fallback (described in implementation)

## 4. Output

The system returns posts in a rich JSON format, with nested info for owner, category, and topic.
