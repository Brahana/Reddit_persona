import os
import sys
import re
import time
import json
from pathlib import Path
from typing import List, Dict
import praw
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'RedditPersonaScript/0.1')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

OUTPUT_DIR = Path('output')
OUTPUT_DIR.mkdir(exist_ok=True)


def extract_username_from_url(url: str) -> str:
    match = re.search(r"reddit.com/user/([\w-]+)/?", url)
    if not match:
        raise ValueError("Invalid Reddit user profile URL.")
    return match.group(1)


def get_reddit_instance():
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )


def fetch_user_content(username: str, limit: int = 100) -> Dict[str, List[Dict]]:
    reddit = get_reddit_instance()
    user = reddit.redditor(username)
    posts = []
    comments = []
    for submission in user.submissions.new(limit=limit):
        posts.append({
            'title': submission.title,
            'selftext': submission.selftext,
            'url': submission.url,
            'permalink': f"https://www.reddit.com{submission.permalink}",
            'created_utc': submission.created_utc
        })
    for comment in user.comments.new(limit=limit):
        comments.append({
            'body': comment.body,
            'link_permalink': f"https://www.reddit.com{comment.permalink}",
            'created_utc': comment.created_utc
        })
    return {'posts': posts, 'comments': comments}


def build_persona_with_llm(username: str, user_data: Dict[str, List[Dict]]) -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError("OpenAI API key not set in environment.")
    openai.api_key = OPENAI_API_KEY
    # Prepare prompt
    prompt = f"""
Given the following Reddit user's posts and comments, build a detailed user persona. For each characteristic, cite the post or comment (with its URL) that supports it. Format the output as a persona profile with citations.

Reddit Username: {username}

Posts:
"""
    for post in user_data['posts']:
        prompt += f"- Title: {post['title']}\n  Text: {post['selftext']}\n  URL: {post['permalink']}\n"
    prompt += "\nComments:\n"
    for comment in user_data['comments']:
        prompt += f"- {comment['body']}\n  URL: {comment['link_permalink']}\n"
    prompt += "\nPersona Profile (with citations):\n"
    # Call OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.7
    )
    return response['choices'][0]['message']['content']


def save_persona(username: str, persona: str):
    out_path = OUTPUT_DIR / f"{username}_persona.txt"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(persona)
    print(f"Persona saved to {out_path}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python reddit_persona.py <reddit_user_profile_url>")
        sys.exit(1)
    url = sys.argv[1]
    username = extract_username_from_url(url)
    print(f"Fetching data for Reddit user: {username}")
    user_data = fetch_user_content(username)
    print(f"Fetched {len(user_data['posts'])} posts and {len(user_data['comments'])} comments.")
    persona = build_persona_with_llm(username, user_data)
    save_persona(username, persona)

if __name__ == "__main__":
    main()
