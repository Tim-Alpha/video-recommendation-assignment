import json
import os
from typing import List, Dict, Any
from openai import OpenAI
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt, wait_exponential

# Set up logging for debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_flattened_post_data(data):
    """
    Extracts and flattens post data into a simplified structure.
    """
    post_summary = data.get("post_summary", {})
    
    # Log the entire input data for debugging
    logging.info(f"Input data: {json.dumps(data, indent=2)}")
    logging.info(f"Post summary structure: {post_summary}")
    
    # Initialize default values
    actions = []
    audio_specifics = []
    description = ""
    emotions = []
    main_gender = ""
    estimated_duration = ""
    keywords = []
    no_of_persons = 0
    targeted_audience = []
    topics = {}
    visual_elements = []
    quality_indicators = []
    psychological_views = []

    # Handle post_summary as a dictionary
    try:
        if post_summary and isinstance(post_summary, dict):
            # Handle actions
            actions = post_summary.get("actions", {}).get("main_actions", []) or post_summary.get("actions", {}).get("key_actions", [])
            
            # Handle audio_elements
            audio_specifics = post_summary.get("audio_elements", {}).get("specifics", []) or post_summary.get("audio_elements", {}).get("specific_audio_features", [])
            
            description = post_summary.get("description", "")
            
            # Handle emotions
            emotions = post_summary.get("emotions", {}).get("primary_emotions", []) or post_summary.get("emotions", {}).get("emotional_content", []) or post_summary.get("emotions", {}).get("moods", [])
            
            # Handle entities for main character gender
            entities = post_summary.get("entities", {})
            main_gender = entities.get("main_character", {}).get("gender", "") or entities.get("main_entity", {}).get("gender", "") or entities.get("speaker", {}).get("gender", "")
            
            estimated_duration = post_summary.get("estimated_duration", "")
            
            # Extract keywords
            keywords = [kw["keyword"] for kw in post_summary.get("keywords", []) if isinstance(kw, dict) and "keyword" in kw]
            
            no_of_persons = post_summary.get("no_of_person_in_video", 0)
            
            # Handle targeted_audience
            targeted_audience = post_summary.get("targeted_audiance", {}).get("groups", []) or post_summary.get("targeted_audiance", {}).get("relevant_groups", [])
            
            topics = post_summary.get("topics_of_video", {})
            
            # Handle visual_elements
            visual_elements = post_summary.get("visual_elements_of_video", {}).get("notable_features", []) or post_summary.get("visual_elements_of_video", {}).get("notable_visuals", []) or post_summary.get("visual_elements_of_video", {}).get("notable_elements", [])
            
            # Handle quality_indicators
            quality_indicators = post_summary.get("quality_indicators", {}).get("marks", []) or post_summary.get("quality_indicators", {}).get("video_quality", []) or post_summary.get("quality_indicators", {}).get("indicators", [])
            
            # Handle psychological_views
            psychological_views = post_summary.get("psycological_view_of_video", {}).get("traits", []) or post_summary.get("psycological_view_of_video", {}).get("traits", [])
        else:
            logging.warning("Post summary is empty or not a valid dictionary")
    except Exception as e:
        logging.error(f"Error processing post_summary: {str(e)}")
        # Continue with default values

    flat_json = {
        "id": data.get("id"),
        "description": data.get("category", {}).get("description", ""),
        "slug": data.get("slug"),
        "title": data.get("title"),
        "upvote_count": data.get("upvote_count"),
        "view_count": data.get("view_count"),
        "average_rating": data.get("average_rating"),
        "username": data.get("username"),
        "main_actions": actions,
        "audio_element_specifics": audio_specifics,
        "post_description": description,
        "primary_emotions": emotions,
        "main_character_gender": main_gender,
        "estimated_duration": estimated_duration,
        "keywords": keywords,
        "no_of_person_in_video": no_of_persons,
        "targeted_audience": targeted_audience,
        "video_theme": topics.get("theme", "") or topics.get("main_topic", "") or topics.get("main", ""),
        "visual_storytelling": topics.get("visual_storytelling", "") or topics.get("sub_topics", ""),
        "emotional_conflicts": topics.get("emotional_conflicts", ""),
        "visual_elements": visual_elements,
        "quality_indicators": quality_indicators,
        "psychological_views": psychological_views
    }
    return flat_json

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def call_openai_api(client, model, messages, temperature):
    """
    Makes a call to the OpenAI API with retry logic.
    """
    return client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )

def llm_summarizer(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Uses GPT API to summarize post data and classify into one of 25 categories.
    Returns a dictionary with summary and category.
    """
    categories = [
        "Education", "Entertainment", "Technology", "Lifestyle", "Travel", 
        "Food", "Health", "Fitness", "Finance", "News", "Comedy", "Gaming", 
        "Music", "Art", "Fashion", "Business", "Science", "History", 
        "Motivation", "Sports", "Politics", "Tutorial", "Review", "Vlog", "DIY"
    ]
    
    summary_data = {
        "description": data.get("description", ""),
        "main_actions": data.get("main_actions", []),
        "audio_element_specifics": data.get("audio_element_specifics", []),
        "post_description": data.get("post_description", ""),
        "primary_emotions": data.get("primary_emotions", []),
        "targeted_audience": data.get("targeted_audience", []),
        "video_theme": data.get("video_theme", ""),
        "visual_storytelling": data.get("visual_storytelling", ""),
        "emotional_conflicts": data.get("emotional_conflicts", ""),
        "visual_elements": data.get("visual_elements", []),
        "quality_indicators": data.get("quality_indicators", []),
        "psychological_views": data.get("psychological_views", [])
    }
    
    prompt = f"""
    Summarize the following post data in 2-3 sentences and classify it into exactly ONE of these categories: {', '.join(categories)}.
    Ensure the response is a valid JSON object with 'summary' and 'category' fields, and nothing else.
    
    Post Data:
    {json.dumps(summary_data, indent=2)}
    
    Response format:
    {{"summary": "Your summary here", "category": "One of the categories"}}
    """
    
    try:
        if not os.getenv("OPENAI_API_KEY"):
            logging.error(f"OPENAI_API_KEY environment variable is not set for post ID: {data.get('id')}")
            return {
                "summary": "Failed to generate summary due to missing API key.",
                "category": "Entertainment"
            }
        
        client = OpenAI()
        logging.info(f"Sending API request for post ID: {data.get('id')}")
        response = call_openai_api(
            client=client,
            model="gpt-4.1-nano",  # Updated to a valid model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes content and categorizes it accurately. Always return a valid JSON object."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        # Log the raw response content for debugging
        raw_content = response.choices[0].message.content
        logging.info(f"Received API response for post ID: {data.get('id')}: {raw_content}")
        
        # Strip whitespace and handle code fences
        raw_content = raw_content.strip()
        if raw_content.startswith("```json"):
            raw_content = raw_content[7:-3].strip()
        
        if not raw_content:
            raise ValueError("Empty response content from API")
        
        # Attempt to parse JSON
        try:
            result = json.loads(raw_content)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse API response as JSON for post ID: {data.get('id')}: {raw_content}")
            raise ValueError(f"Invalid JSON response: {str(e)}")
        
        # Validate the result structure
        if not isinstance(result, dict) or "summary" not in result or "category" not in result:
            raise ValueError("Response does not contain required 'summary' and 'category' fields")
        
        # Ensure category is valid
        if result["category"] not in categories:
            logging.warning(f"Invalid category '{result['category']}' received for post ID: {data.get('id')}, defaulting to 'Entertainment'")
            result["category"] = "Entertainment"
        
        return result
    
    except Exception as e:
        logging.error(f"API error for post ID: {data.get('id')}: {str(e)}")
        return {
            "summary": "Failed to generate summary due to API error.",
            "category": "Entertainment"
        }

def process_post(post):
    """
    Processes a single post, extracts required fields, summarizes data, and returns the updated post.
    """
    logging.info(f"Processing post ID: {post.get('id')}")
    flat_data = extract_flattened_post_data(post)
    
    selected_fields = {
        "id": flat_data.get("id"),
        "upvote_count": flat_data.get("upvote_count"),
        "view_count": flat_data.get("view_count"),
        "average_rating": flat_data.get("average_rating"),
        "username": flat_data.get("username"),
        "keywords": flat_data.get("keywords", []),
        "no_of_person_in_video": flat_data.get("no_of_person_in_video"),
        "estimated_duration": flat_data.get("estimated_duration"),
        "main_character_gender": flat_data.get("main_character_gender")
    }
    
    llm_result = llm_summarizer(flat_data)
    
    return {
        **selected_fields,
        "summary": llm_result["summary"],
        "category": llm_result["category"]
    }

def process_posts(posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Processes each post in parallel, extracts required fields, summarizes remaining data,
    and returns an array of updated posts.
    """
    updated_posts = []
    with ThreadPoolExecutor(max_workers=5) as executor:  # Adjust max_workers based on system
        future_to_post = {executor.submit(process_post, post): post for post in posts}
        for future in as_completed(future_to_post):
            try:
                updated_posts.append(future.result())
            except Exception as e:
                logging.error(f"Error processing post: {str(e)}")
    return updated_posts

def main():
    """
    Main function to load posts, process them, and store updated summaries.
    """
    from database_manager import load_all_posts, store_updated_post_summaries
    logging.info("Starting main function")
    data = load_all_posts()
    posts = data.get("posts", [])
    logging.info(f"Loaded {len(posts)} posts")
    
    updated_posts = []
    try:
        updated_posts = process_posts(posts)
        store_updated_post_summaries(updated_posts)
        print(json.dumps(updated_posts, indent=2))
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt detected. Saving progress...")
        store_updated_post_summaries(updated_posts)  # Save any processed posts
        logging.info("Progress saved. Exiting.")
    return updated_posts

if __name__ == "__main__":
    main()