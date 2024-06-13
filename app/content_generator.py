from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, base
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from typing import List, Tuple
from fastapi import HTTPException
import re
import json
import mistletoe
from langchain_core.pydantic_v1 import BaseModel, Field
import dotenv
import tomllib
import logging

from .compare_text_similarity import TextComparer

dotenv.load_dotenv()

llm = ChatOpenAI()


class FAQ(BaseModel):
    question: str = Field(description="the question")
    answer: str = Field(description="answer to the question")


class ContentGenerator:
    def __init__(self) -> None:
        with open("app/prompts.toml", "rb") as f:
            prompts = tomllib.load(f)["prompts"]
        self.prompts = {
            key: (value["speaker"], value["prompt_text"])
            for key, value in prompts.items()
        }

    def set_up_runnable(self, prompt_messages: List[Tuple[str]]) -> base.Runnable:
        prompt = ChatPromptTemplate.from_messages(prompt_messages)
        runnable = prompt | llm | StrOutputParser()
        return runnable

    def get_wordcount(self, text: str) -> int:
        return len(text.split(" "))

    def increase_wordcount(self, info: dict) -> dict:
        runnable = self.set_up_runnable(
            [
                self.prompts["generate_article_system"],
                self.prompts["generate_article_human"],
                self.prompts["generated_article_ai"],
                self.prompts["increase_wordcount_human"],
            ]
        )
        wordcount = self.get_wordcount(info["generated_article"])
        if wordcount < 500:
            return RunnablePassthrough() | RunnablePassthrough.assign(
                generated_article=runnable
            )
        return info

    def remove_key_from_outputs(self, ouputs: List[dict], key_name: str) -> None:
        for i in range(len(ouputs)):
            ouputs[i].pop(key_name)

    @property
    def relevant_service_page_chain(self) -> base.Runnable:
        return RunnablePassthrough.assign(
            webpage=self.set_up_runnable(
                [self.prompts["get_relevant_service_page_human"]]
            )
        )

    def convert_additional_keywords_to_list(self, info) -> dict:
        additional_keywords = info["additional_keywords"]
        additional_keywords.replace("\n", "")
        # Use regular expression to split by numbers followed by a period and a space
        split_keywords = re.split(r"\d+\.\s*", additional_keywords)

        # Remove any empty strings that may result from the split
        split_keywords = [item for item in split_keywords if item]
        info["additional_keywords"] = split_keywords
        return info

    @property
    def additional_keywords_chain(self) -> base.Runnable:

        return (
            self.relevant_service_page_chain
            | RunnablePassthrough.assign(
                additional_keywords=self.set_up_runnable(
                    [self.prompts["get_additional_keywords_human"]]
                )
            )
            | RunnableLambda(self.convert_additional_keywords_to_list)
        )

    @property
    def generate_article_chain(self) -> base.Runnable:
        return self.additional_keywords_chain | RunnablePassthrough.assign(
            generated_article=self.set_up_runnable(
                [
                    self.prompts["generate_article_system"],
                    self.prompts["generate_article_human"],
                ]
            )
        )

    @property
    def optimize_article_length_chain(self) -> base.Runnable:
        return self.generate_article_chain | RunnableLambda(self.increase_wordcount)

    @property
    def generate_meta_description_chain(self) -> base.Runnable:
        return self.optimize_article_length_chain | RunnablePassthrough.assign(
            meta_description=self.set_up_runnable(
                [
                    self.prompts["meta_description_system"],
                    self.prompts["meta_description_human"],
                ]
            )
        )

    def format_articles_in_html(self, articles: List[dict]) -> None:
        for i, article in enumerate(articles):
            as_html = mistletoe.markdown(article["generated_article"])
            articles[i]["generated_article"] = as_html

    def generate_blog_posts(self, inputs: List[dict]) -> List[dict]:
        try:
            articles = self.generate_meta_description_chain.batch(inputs)
        except Exception as e:
            logging.error(f"Error: could not generate articles. {e}")
            raise HTTPException(status_code=500, detail=e)
        self.remove_key_from_outputs(articles, "brand_service_pages")
        self.format_articles_in_html(articles)
        return articles

    def get_character_count(self, text: str) -> int:
        return len(text)

    def decrease_answer_character_count(self, info: dict) -> dict:
        prompt = ChatPromptTemplate.from_messages(
            [
                self.prompts["generate_faq_system"],
                self.prompts["generate_faq_human"],
                self.prompts["generated_faq"],
                self.prompts["decrease_charactercount_human"],
            ]
        )
        runnable = prompt | llm | StrOutputParser()
        answer_character_count = self.get_character_count(info["faq"]["answer"])
        if answer_character_count > 400:
            return RunnablePassthrough() | RunnablePassthrough.assign(faq=runnable)
        return info

    def format_faq_chain_output(self, output: List[dict]) -> List[dict]:
        formatted = []
        for faq in output:
            formatted.append(faq["faq"])
        return formatted

    def check_faq_similarity(self, faqs: List[dict]) -> dict:
        corpus = [x["answer"] for x in faqs]
        text_comparer = TextComparer(corpus)
        return text_comparer.find_groups_of_similar_text()

    @property
    def generate_faq_chain(self) -> base.Runnable:
        prompt = ChatPromptTemplate.from_messages(
            [self.prompts["generate_faq_system"], self.prompts["generate_faq_human"]]
        )
        generate_faq_runnable = prompt | llm | JsonOutputParser(pydantic_object=FAQ)
        return RunnablePassthrough.assign(faq=generate_faq_runnable)

    @property
    def optimize_faq_length_chain(self) -> base.Runnable:
        return self.generate_faq_chain | RunnableLambda(
            self.decrease_answer_character_count
        )

    def format_gerated_faqs(self, generated_faqs: List) -> List[dict[str, str]]:
        faqs = []
        for faq in generated_faqs:
            if type(faq) == str and faq[0] == "{" and faq[-1] == "}":
                faqs.append(json.loads(faq))
            elif type(faq) == dict:
                faqs.append(faq)
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"GPT output did not follow correct formatting. Instead of json, faq was represented as {type(faq)}",
                )
        return faqs

    def generate_faqs(self, inputs: List[dict]) -> dict:
        try:
            generated_faqs = self.format_faq_chain_output(
                self.optimize_faq_length_chain.batch(inputs)
            )
        except Exception as e:
            logging.error(f"Error: could not generate FAQs. {e}")
            raise HTTPException(status_code=500, detail=e)
        generated_faqs = self.format_gerated_faqs(generated_faqs)
        similar_faqs = self.check_faq_similarity(generated_faqs)
        output = {"faqs": generated_faqs, "similarly_worded_faqs": similar_faqs}

        return output
