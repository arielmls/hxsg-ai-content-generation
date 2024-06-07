import dotenv
from fastapi import FastAPI
from typing import List
from .content_generator import ContentGenerator
from .input_formatter import InputFormatter
from .hxsg_brands import HXSGBrand

dotenv.load_dotenv()

app = FastAPI()


@app.get("/")
def root():
    return {"message": "hello world"}


@app.post("/generate_blog_post/")
def generate_blog_post(longtail_keywords: List[str], brand: HXSGBrand):
    content_generator = ContentGenerator()
    input_formatter = InputFormatter()
    inputs = input_formatter.format_inputs(longtail_keywords, brand)
    generated_blog_posts = content_generator.generate_blog_posts(inputs)
    return generated_blog_posts


@app.post("/generate_faq/")
def generate_faq(longtail_keywords: List[str], brand: HXSGBrand):
    content_generator = ContentGenerator()
    input_formatter = InputFormatter()
    inputs = input_formatter.format_inputs(longtail_keywords, brand)
    generated_blog_posts = content_generator.generate_faqs(inputs)
    return generated_blog_posts
