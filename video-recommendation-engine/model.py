import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from implicit.als import AlternatingLeastSquares
import tensorflow as tf
import requests
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sentence_transformers import SentenceTransformer
from sklearn.pipeline import make_pipeline
from scipy.sparse import coo_matrix
from implicit.als import AlternatingLeastSquares
from sklearn.preprocessing import normalize
import faiss
import os
import pickle
from datetime import datetime, date

CACHE_DIR = os.path.join(os.getcwd(), "cache")
USER_TEXT_EMB_FILE = os.path.join(CACHE_DIR, "user_text_embedding.pkl")
POST_TEXT_EMB_FILE = os.path.join(CACHE_DIR, "post_embedding.pkl")
CACHE_DATE_FILE = os.path.join(CACHE_DIR, "cache_date.txt")
INTERACTIONS_FILE = os.path.join(CACHE_DIR, "interactions.pkl")

os.makedirs(CACHE_DIR, exist_ok=True)


def should_recompute_embeddings():
    if not os.path.isfile(USER_TEXT_EMB_FILE) or not os.path.isfile(POST_TEXT_EMB_FILE):
        return True
    if not os.path.isfile(CACHE_DATE_FILE):
        return True
    with open(CACHE_DATE_FILE, "r") as f:
        last_date = f.read().strip()
    try:
        last_cached = datetime.strptime(last_date, "%Y-%m-%d").date()
    except ValueError:
        return True
    return last_cached != date.today()
def is_interactions_cache_valid():
    if not os.path.exists(INTERACTIONS_FILE) or not os.path.exists(CACHE_DATE_FILE):
        return False
    with open(CACHE_DATE_FILE, "r") as f:
        cached_date = f.read().strip()
    return cached_date == str(date.today())

def is_file_cache_valid(file):
    if not os.path.exists(os.path.join(CACHE_DIR, f"{file}.pkl")) or not os.path.exists(CACHE_DATE_FILE):
        return False
    with open(CACHE_DATE_FILE, "r") as f:
        cached_date = f.read().strip()
    return cached_date == str(date.today())

API_BASE = "https://api.socialverseapp.com"
HEADERS = {"Flic-Token": 
"flic_11d3da28e403d182c36a3530453e290add87d0b4a40ee50f17611f180d47956f"}

def fetch_paginated_data_global(endpoint):
    """Fetch all pages of data from API endpoint"""
    all_data = []
    page = 1
    while True:
        response = requests.get(
            f"{API_BASE}{endpoint}?page={page}&page_size=1000",
            headers=HEADERS
        )
        data = response.json()
        
        if data['page_size'] ==0:
            break
        if endpoint=="/users/get_all":
            all_data.extend(data['users'])
        else:
            all_data.extend(data['posts'])
        page += 1
    return pd.DataFrame(all_data)

def fetch_paginated_data(endpoint):
    """Fetch all pages of data from API endpoint"""
    all_data = []
    page = 1
    while True:
        response = requests.get(
            f"{API_BASE}{endpoint}?page={page}&page_size=1000&resonance_algorithm=resonance_algorithm_cjsvervb7dbhss8bdrj89s44jfjdbsjd0xnjkbvuire8zcjwerui3njfbvsujc5if",
        )
        data = response.json()
        
        if data['page_size'] ==0:
            break
        all_data.extend(data['posts'])
        page += 1
    return pd.DataFrame(all_data)

\
if is_interactions_cache_valid()==False:
    print("Fetching data from API...")
    views_df = fetch_paginated_data("/posts/view")
    likes_df = fetch_paginated_data("/posts/like")
    inspires_df = fetch_paginated_data("/posts/inspire")
    rating_df=fetch_paginated_data("/posts/rating")


if is_interactions_cache_valid()==False:

    likes_df['liked'] = 1
    inspires_df['inspired'] = 1

  
    interactions = views_df[['user_id', 'post_id']].copy()

 
    interactions = interactions.merge(
        likes_df[['user_id', 'post_id', 'liked']],
        on=['user_id', 'post_id'],
        how='left'
    )


    interactions = interactions.merge(
        inspires_df[['user_id', 'post_id', 'inspired']],
        on=['user_id', 'post_id'],
        how='left'
    )
    interactions = interactions.merge(
        rating_df[['user_id', 'post_id', 'rating_percent']],
        on=['user_id', 'post_id'],
        how='left'
    )

  
    interactions['liked'] = interactions['liked'].fillna(0).astype(int)
    interactions['inspired'] = interactions['inspired'].fillna(0).astype(int)
    with open(INTERACTIONS_FILE, "wb") as f:
        pickle.dump(interactions, f)
if should_recompute_embeddings()==True:
    with open(INTERACTIONS_FILE, "rb") as f:
        interactions = pickle.load(f)

if is_file_cache_valid("posts_df")==False:

    posts_df = fetch_paginated_data_global("/posts/summary/get")
    with open(os.path.join(CACHE_DIR, "posts_df.pkl"), "wb") as f:
        pickle.dump(posts_df, f)
if is_file_cache_valid("posts_df")==True:
    with open(os.path.join(CACHE_DIR, "posts_df.pkl"), "rb") as f:
        posts_df=pickle.load(f)

if is_file_cache_valid("users_df")==False:

    users_df = fetch_paginated_data_global("/users/get_all")
    with open(os.path.join(CACHE_DIR, "users_df.pkl"), "wb") as f:
        pickle.dump(users_df, f)
if is_file_cache_valid("users_df")==True:
    with open(os.path.join(CACHE_DIR, "users_df.pkl"), "rb") as f:
        users_df=pickle.load(f)





posts_df=posts_df[posts_df["is_available_in_public_feed"]==True]
posts_df=posts_df[["id","topic","slug","title","post_summary","tags"]]

users_df=users_df[["id","gender","role","bio","user_type","hourly_rate","isVerified","share_count","total_inspired_user_count","daily_login_streak", 'post_count', 'following_count', 'follower_count',"latitude","longitude"]]


users_df["combined_text"] = (
    "bio:"+users_df["bio"].fillna('') + ' ' +
    "role:"+users_df["role"].fillna('') + ' ' +
    "user_type"+users_df["user_type"].fillna('')
)
users_df


if should_recompute_embeddings():
    sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
    user_text_embedding = sbert_model.encode(users_df["combined_text"].tolist(), 
    show_progress_bar=True)
    with open(USER_TEXT_EMB_FILE, "wb") as f:
        pickle.dump(user_text_embedding, f)
else:
    with open(USER_TEXT_EMB_FILE, "rb") as f:
        user_text_embedding = pickle.load(f)
pca=PCA(n_components=119)
user_text_embedding=pca.fit_transform(user_text_embedding)


numerical_cols_user = [
    "hourly_rate", "share_count", "post_count", "follower_count",
    "following_count", "daily_login_streak", "total_inspired_user_count",
    "latitude", "longitude"
]
users_df[numerical_cols_user] = users_df[numerical_cols_user].replace('', 
np.nan)

users_df[numerical_cols_user] = users_df[numerical_cols_user].apply(pd.to_numeric, errors='coerce')
user_numeric = users_df[numerical_cols_user].fillna(0)
scaler = MinMaxScaler()  
user_numeric_embedding = scaler.fit_transform(user_numeric)


user_embedding = np.hstack([
    user_text_embedding,   
    user_numeric_embedding          
])
user_embedding_df = pd.DataFrame(user_embedding)
user_embedding_df.insert(0,"User_id",users_df["id"].values)

def safe_dict(d):
    return d if isinstance(d, dict) else {}

def flatten_dict_kv(d, parent_key=''):
    items = []
    if isinstance(d, dict):
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict_kv(v, new_key))
            elif isinstance(v, list):
                for i in v:
                    items.extend(flatten_dict_kv(i, new_key))
            else:
                if v is not None:
                    items.append(f"{new_key}: {str(v)}")
    elif isinstance(d, list):
        for i in d:
            items.extend(flatten_dict_kv(i, parent_key))
    elif isinstance(d, str):
        items.append(f"{parent_key}: {d}")
    return items

def extract_flat_kv(summary):
    summary = summary if isinstance(summary, dict) else {}
    flattened = flatten_dict_kv(summary)
    return " ".join(flattened)

posts_df['post_summary_text'] = posts_df['post_summary'].apply(extract_flat_kv)
posts_df["topic_text"]=posts_df['topic'].apply(extract_flat_kv)

posts_df["combined_text"] = (
    "topic: " + posts_df["topic_text"].fillna('') + ' ' +
    "slug: " + posts_df["slug"].fillna('') + ' ' +
    "title: " + posts_df["title"].fillna('') + ' ' +
    "summary: " + posts_df["post_summary_text"].fillna('') + ' ' 
)

if should_recompute_embeddings:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    post_text_embedding = model.encode(posts_df["combined_text"].tolist(), 
    show_progress_bar=True)
    with open(POST_TEXT_EMB_FILE, "wb") as f:
        pickle.dump(post_text_embedding, f)

    with open(CACHE_DATE_FILE, "w") as f:
        f.write(str(date.today()))
else:
    with open(POST_TEXT_EMB_FILE, "rb") as f:
        post_text_embedding = pickle.load(f)

pca_post=PCA(n_components=128)
post_text_embedding=pca_post.fit_transform(post_text_embedding)

post_embedding_df = pd.DataFrame(post_text_embedding)
post_embedding_df.insert(0,"Post_id",posts_df["id"].values)

interactions["rating_percent"] = interactions["rating_percent"].fillna(0) / 100
interactions["interaction"] = (
    1.5 * interactions["liked"] +
    1.5 * interactions["inspired"] +
    2.0 * interactions["rating_percent"]
)
interactions_df = interactions[interactions["interaction"] > 0]
interactions_df

user_encoder = LabelEncoder()
item_encoder = LabelEncoder()

interactions_df["user_idx"] = user_encoder.fit_transform(interactions_df["user_id"])
interactions_df["post_idx"] = item_encoder.fit_transform(interactions_df["post_id"])

user_post_matrix = coo_matrix(
    (interactions_df["interaction"], 
     (interactions_df["user_idx"], interactions_df["post_idx"]))
)

als_model = AlternatingLeastSquares(
    factors=128,  
    regularization=0.01, 
    iterations=30,  
    use_gpu=False,
    alpha=15, 
)
als_model.fit(user_post_matrix)

user_embeddings_als = als_model.user_factors  
post_embeddings_als = als_model.item_factors
user_embedding_als_df = pd.DataFrame(user_embeddings_als)
user_embedding_als_df.insert(0, "user_id", user_encoder.inverse_transform(range(len(user_embedding_als_df))))

post_embedding_als_df = pd.DataFrame(post_embeddings_als)
post_embedding_als_df.insert(0, "post_id", item_encoder.inverse_transform(range(len(post_embedding_als_df))))

user_embedding_df_normalized = user_embedding_df.copy()
user_embedding_df_normalized.iloc[:, 1:] = normalize(user_embedding_df_normalized.iloc[:, 1:], axis=1)

user_embedding_als_df_normalized = user_embedding_als_df.copy()
user_embedding_als_df_normalized.iloc[:, 1:] = normalize(user_embedding_als_df_normalized.iloc[:, 1:], axis=1)

post_embedding_df_normalized = post_embedding_df.copy()
post_embedding_df_normalized.iloc[:, 1:] = normalize(post_embedding_df_normalized.iloc[:, 1:], axis=1)

post_embedding_als_df_normalized = post_embedding_als_df.copy()
post_embedding_als_df_normalized.iloc[:, 1:] = normalize(post_embedding_als_df_normalized.iloc[:, 1:], axis=1)

user_hybrid_embeddings = {}

for user_id in user_embedding_df_normalized["User_id"].values:
    sbert_row = user_embedding_df_normalized[user_embedding_df_normalized["User_id"] == user_id].drop(columns=["User_id"]).iloc[0].to_numpy()

    if user_id in user_embedding_als_df_normalized["user_id"].values:
        als_row = user_embedding_als_df_normalized[user_embedding_als_df_normalized["user_id"] == user_id].drop(columns=["user_id"]).iloc[0].to_numpy()
        final_row = 0.8 * sbert_row + 0.2 * als_row  
    else:
        final_row = sbert_row

    user_hybrid_embeddings[user_id] = final_row


post_hybrid_embeddings = {}

for post_id in post_embedding_df_normalized["Post_id"].values:
    sbert_row = post_embedding_df_normalized[post_embedding_df_normalized["Post_id"] == post_id].drop(columns=["Post_id"]).iloc[0].to_numpy()

    if post_id in post_embedding_als_df_normalized["post_id"].values:
        als_row = post_embedding_als_df_normalized[post_embedding_als_df_normalized["post_id"] == post_id].drop(columns=["post_id"]).iloc[0].to_numpy()
        final_row = 0.8 * sbert_row + 0.2 * als_row  
    else:
        final_row = sbert_row

    post_hybrid_embeddings[post_id] = final_row



def build_faiss_index_cosine(post_hybrid_embeddings):
    post_ids = list(post_hybrid_embeddings.keys())
    post_vectors = np.array([post_hybrid_embeddings[pid] for pid in post_ids]).astype('float32')
    post_vectors = normalize(post_vectors, axis=1)

    index = faiss.IndexFlatIP(post_vectors.shape[1])
    index.add(post_vectors)

    return index, post_ids

def recommend_posts_faiss_cosine(user_id, user_hybrid_embeddings, post_hybrid_embeddings, interactions_df, top_k=100):
    if user_id not in user_hybrid_embeddings:
        print(f"User ID {user_id} not found in hybrid embeddings.")
        return []


    interacted_posts = set(interactions_df[interactions_df["user_id"] == user_id]["post_id"].values)

    filtered_post_hybrid_embeddings = {
        pid: emb for pid, emb in post_hybrid_embeddings.items() if pid not in interacted_posts
    }


    index, post_ids = build_faiss_index_cosine(filtered_post_hybrid_embeddings)

  
    user_vector = normalize([user_hybrid_embeddings[user_id]]).astype('float32')

   
    distances, indices = index.search(user_vector, top_k)

  
    results = []
    for i in range(len(indices[0])):
        post_id = post_ids[indices[0][i]]
        score = distances[0][i]
        results.append((post_id, score))

    return results





def get_top_similar_posts_to_project(project_name, post_embedding_df, top_k=500):
  
    model = SentenceTransformer("all-MiniLM-L6-v2")
    project_embedding = model.encode([project_name])[0]
    project_embedding = normalize([project_embedding], axis=1).astype('float32')
    project_embedding=pca_post.transform(project_embedding)
    project_embedding_df=pd.DataFrame(project_embedding)

  
    project_embedding = project_embedding_df.iloc[[0]].to_numpy().astype('float32')


    post_ids = post_embedding_df["Post_id"].values
    post_vectors = post_embedding_df.drop(columns=["Post_id"]).values.astype('float32')
    post_vectors = normalize(post_vectors, axis=1)

    index = faiss.IndexFlatIP(post_vectors.shape[1])
    index.add(post_vectors)

    distances, indices = index.search(project_embedding, top_k)
    similar_post_ids = [post_ids[i] for i in indices[0]]
    return similar_post_ids

def build_faiss_index_cosine_from_pool(post_ids, post_hybrid_embeddings):
    post_vectors = np.array([post_hybrid_embeddings[pid] for pid in post_ids]).astype('float32')
    post_vectors = normalize(post_vectors, axis=1)

    index = faiss.IndexFlatIP(post_vectors.shape[1])
    index.add(post_vectors)
    return index, post_ids

def final_recommend_from_project(user_id, project_name, user_hybrid_embeddings, post_hybrid_embeddings,
                                 post_embedding_df, interactions_df, top_k_pool=500, top_k_final=100):
    if user_id not in user_hybrid_embeddings:
        print(f"User ID {user_id} not found.")
        return []

  
    similar_post_ids = get_top_similar_posts_to_project(project_name, post_embedding_df, top_k=top_k_pool)

 
    interacted_post_ids = set(interactions_df[interactions_df["user_id"] == user_id]["post_id"].values)
    filtered_post_ids = [pid for pid in similar_post_ids if pid not in interacted_post_ids]

    if not filtered_post_ids:
        print("No posts left after filtering interactions.")
        return []


    index, filtered_post_ids = build_faiss_index_cosine_from_pool(filtered_post_ids, post_hybrid_embeddings)
    user_vector = normalize([user_hybrid_embeddings[user_id]]).astype('float32')
    distances, indices = index.search(user_vector, top_k_final)


    results = []    
    for i in range(len(indices[0])):
        post_id = filtered_post_ids[indices[0][i]]
        score = distances[0][i]
        results.append((post_id, score))

  
    return results
# final_recommend_from_project(3, "motivation", user_hybrid_embeddings, post_hybrid_embeddings,post_embedding_df, interactions_df, top_k_pool=500, top_k_final=100)
