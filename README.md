# Reddit User Persona Generator

This script scrapes a Reddit user's posts and comments, then generates a user persona using an LLM. Each persona trait is cited with the relevant Reddit post or comment.

## Setup

1. Clone this repository.
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Obtain Reddit API credentials (see below).
4. (Optional) Obtain OpenAI API key for LLM persona generation.

## Reddit API Credentials
- Create an app at https://www.reddit.com/prefs/apps
- Set type to "script"
- Note your client_id, client_secret, and username/password

## Usage

```powershell
python reddit_persona.py <reddit_user_profile_url>
```

Example:
```powershell
python reddit_persona.py https://www.reddit.com/user/kojied/
```

- Output persona will be saved in the `output/` directory.

## Sample Output
- See `output/kojied_persona.txt` and `output/Hungry-Move-6603_persona.txt` after running the script.

## Notes
- Follows PEP-8 guidelines.
- LLM usage is optional; you can use OpenAI or a local model.
- **Important:** This script requires an OpenAI API key with available quota for persona generation. If you encounter a `RateLimitError` or quota error, please use your own OpenAI API key with sufficient credits. The Reddit scraping functionality works regardless of OpenAI quota.
