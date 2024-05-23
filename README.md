# hxsg-ai-content-generation
## Purpose
Generate blog posts and Q&As to improve the SEO of the HxSG service company websites

## Run the App Locally
Install requirements
`pip install -r "requirements.txt"`

Run FastAPI app
`fastapi dev app/main.py`

Open swagger docs in browser
http://127.0.0.1:8000/docs


## Endpoints
### /generate_haller_blog_post/
Generates blog posts for Haller Enterprises
*Input:* (list of strings) List of long tail keywords to use as topics for geenrated blog posts

### /generate_haller_faq/
Generates Q&As for Haller Enterprises
*Input:* (list of strings) List of long tail keywords to use as topics for short Q&As