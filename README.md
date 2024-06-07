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
### /generate_blog_post/
Generates blog posts 
#### Input:
- longtail_keywords: (list of strings) List of long tail keywords to use as topics for geenrated blog posts
- brand: (string) one of "Gem Plumbing and Heating", "Haller Enterprises", "Universe Home Services"

### /generate_faq/
Generates shorter Q&As 
#### Input:
- longtail_keywords:  (list of strings) List of long tail keywords to use as topics for short Q&As
- brand: (string) one of "Gem Plumbing and Heating", "Haller Enterprises", "Universe Home Services"