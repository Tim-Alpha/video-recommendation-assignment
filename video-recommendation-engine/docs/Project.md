# Video Recommendation System Documentation

## Overview

The video recommendation system uses a Graph Neural Network (GNN) to analyze user-content interactions and provide personalized recommendations. The system is built using PyTorch and PyTorch Geometric, with a heterogeneous graph structure that captures different types of interactions between users and content.

## Architecture

### Graph Structure

The recommendation system uses a heterogeneous graph with:

- **Nodes**: Users and Posts (videos)
- **Edges**: 
  - User → Post interactions (viewed, liked, inspired, rated)
  - Post → User reverse interactions
  - User → User similarity connections
  - Post → Post similarity connections

### Model Architecture

The `HeteroGNNRecommender` model consists of:

1. **Feature Embedding Layers**:
   - User features are embedded using a linear layer with batch normalization
   - Post features are embedded using a category embedding and numerical feature normalization

2. **Graph Convolution Layers**:
   - Multiple heterogeneous graph convolution layers that aggregate information across different edge types
   - Uses Graph Attention Networks (GAT) for user-post interactions
   - Uses GraphSAGE for similarity edges

3. **Prediction Layers**:
   - User and post projections
   - Interaction prediction using element-wise multiplication
   - Cold start prediction using mood embeddings

## Recommendation Approaches

### Personalized Recommendations

For existing users, the system:
1. Retrieves the user's node embedding from the GNN
2. Computes interaction scores with all post embeddings
3. Ranks posts by predicted interaction score
4. Filters out already seen content
5. Applies category filtering if requested
6. Returns the top-K recommendations

### Cold Start Recommendations

For new users, the system:
1. Uses mood-based embeddings as a proxy for user preferences
2. Computes compatibility scores between mood embeddings and post embeddings
3. Ranks posts by predicted compatibility
4. Applies category filtering if requested
5. Returns the top-K recommendations

## Data Flow

1. **Data Collection**:
   - User interaction data is collected from external APIs
   - Data includes views, likes, inspires, and ratings

2. **Data Processing**:
   - Interactions are normalized and weighted
   - Timestamps are converted to recency scores
   - Features are normalized

3. **Graph Construction**:
   - User and post nodes are created
   - Interaction edges are added with appropriate weights
   - Similarity edges are computed based on feature similarity

4. **Model Training**:
   - The GNN is trained to predict interaction strengths
   - Early stopping is used to prevent overfitting
   - The best model is saved for inference

5. **Recommendation Generation**:
   - User queries are processed through the API
   - Recommendations are generated using the trained model
   - Results are cached for performance
   - Recommendations are enriched with metadata from the database

## Performance Considerations

- **Caching**: Recommendations are cached with a configurable TTL
- **Pagination**: Results are paginated for efficient delivery
- **Background Processing**: Data collection runs in the background
- **Batch Processing**: Database operations are batched for efficiency


