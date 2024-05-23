# hxsg-ai-content-generation
## Purpose
Generate blog posts and Q&As to improve the SEO of the HxSG service company websites

## Run the App Locally
1. Clone the repo
2. Create a .env file in the root directory with your Open AI API key
```
OPENAI_API_KEY=your_open_ai_api_key_here
```
3. Install requirements
`pip install -r "requirements.txt"`
3. Run FastAPI app
`fastapi dev app/main.py`
4. Open swagger docs in browser
http://127.0.0.1:8000/docs


## Endpoints
### /generate_haller_blog_post/
Generates blog posts for Haller Enterprises
*Input:* (list of strings) List of long tail keywords to use as topics for geenrated blog posts

### /generate_haller_faq/
Generates Q&As for Haller Enterprises
*Input:* (list of strings) List of long tail keywords to use as topics for short Q&As