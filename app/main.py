import dotenv
import os
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


@app.post("/generate_haller_blog_post/")
def generate_haller_blog_post(longtail_keywords: List[str]):
    content_generator = ContentGenerator()
    input_formatter = InputFormatter()
    inputs = input_formatter.format_inputs(longtail_keywords, HXSGBrand.HALLER)
    generated_blog_posts = content_generator.generate_blog_posts(inputs)
    return generated_blog_posts

@app.post("/generate_haller_faq/")
def generate_haller_blog_post(longtail_keywords: List[str]):
    content_generator = ContentGenerator()
    input_formatter = InputFormatter()
    inputs = input_formatter.format_inputs(longtail_keywords, HXSGBrand.HALLER)
    generated_blog_posts = content_generator.generate_faqs(inputs)
    return generated_blog_posts
