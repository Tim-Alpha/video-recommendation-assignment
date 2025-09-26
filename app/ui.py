import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/feed"

st.set_page_config(page_title="🎬 Socialverse Recommender", layout="wide")
st.title("🎬 Socialverse Video Recommender")

username = st.text_input("Enter your username:")

categories = ["", "Education", "Motivation", "Entertainment", "Crypto", "Spiritual", "Lifestyle"]
project_code = st.selectbox("Choose a category (optional):", categories)

if st.button("Get Recommendations"):
    if username:
        params = {"username": username}
        if project_code:
            params["project_code"] = project_code

        try:
            response = requests.get(API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            recs = data.get("recommendations", [])

            if recs:
                st.success(f"Found {len(recs)} recommendations:")

                for post in recs:
                    with st.container():
                        st.markdown("---")
                        st.subheader(post.get("title", "Untitled"))
                        st.write(f" Category: {post.get('category', 'N/A')}")
                        st.write(f" Mood: {post.get('mood', 'N/A')}")
                        if isinstance(post.get("category_info"), dict):
                            cat_info = post["category_info"]
                            st.image(cat_info.get("image_url", ""), width=100, caption=cat_info.get("name", ""))
                        if post.get("link"):
                            st.markdown(f"[▶️ Watch Video]({post['link']})")
            else:
                st.info("No recommendations found for this user/category.")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to backend: {e}")
    else:
        st.warning("Please enter a username.")
