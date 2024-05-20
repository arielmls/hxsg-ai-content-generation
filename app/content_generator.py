from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from typing import List
import json
from langchain_core.pydantic_v1 import BaseModel, Field
import dotenv
import tomllib

from .compare_text_similarity import TextComparer
from .hxsg_brands import HXSGBrand

dotenv.load_dotenv()

llm = ChatOpenAI()

class FAQ(BaseModel):
    question: str = Field(description="the question")
    answer: str = Field(description="answer to the question")


class ContentGenerator:
    def __init__(self) -> None:
        with open("app/prompts.toml", "rb") as f:
            prompts = tomllib.load(f)["prompts"]
        self.prompts = {key:(value["speaker"], value["prompt_text"]) for key,value in prompts.items()}

    def set_up_runnable(self, prompt_messages):
        prompt = ChatPromptTemplate.from_messages(prompt_messages)
        runnable = prompt | llm | StrOutputParser()
        return runnable

    def increase_wordcount(self, info):
        prompt = ChatPromptTemplate.from_messages(
            [
                self.prompts["generate_article_system"],
                self.prompts["generate_article_human"],
                self.prompts["generated_article_ai"],
                self.prompts["increase_wordcount_human"],
            ]
        )
        runnable = prompt | llm | StrOutputParser()
        wordcount = len(info["generated_article"].split(" "))
        if wordcount < 500:
            return RunnablePassthrough() | RunnablePassthrough.assign(
                generated_article=runnable
            )
        return info

    def remove_key_from_outputs(self, ouputs:List[dict], key_name: str) -> None:
        new_outputs = []
        for i in range(len(ouputs)):
            ouputs[i].pop(key_name)
            

    def generate_blog_posts(self, inputs: List[dict], output_filepath:str =False):
        relevant_service_page_chain = RunnablePassthrough.assign(
            webpage=self.set_up_runnable([self.prompts["get_relevant_service_page_human"]])
        )
        additional_keywords_chain = (
            relevant_service_page_chain
            | RunnablePassthrough.assign(
                additional_keywords=self.set_up_runnable(
                    [self.prompts["get_additional_keywords_human"]]
                )
            )
        )
        generate_article_chain = additional_keywords_chain | RunnablePassthrough.assign(
            generated_article=self.set_up_runnable(
                [self.prompts["generate_article_system"], self.prompts["generate_article_human"]]
            )
        )
        optimize_article_length_chain = generate_article_chain | RunnableLambda(
            self.increase_wordcount
        )
        generate_meta_description_chain = (
            optimize_article_length_chain
            | RunnablePassthrough.assign(
                meta_description=self.set_up_runnable(
                    [
                        self.prompts["meta_description_system"],
                        self.prompts["meta_description_human"],
                    ]
                )
            )
        )

        outputs = generate_meta_description_chain.batch(inputs)
        self.remove_key_from_outputs(outputs, "brand_service_pages")
        if output_filepath:
            with open(output_filepath, "w") as outfile:
                json.dump(outputs, outfile, indent=6)

        return outputs

    def decrease_answer_character_count(self, info):
        prompt = ChatPromptTemplate.from_messages(
            [
                self.prompts["generate_faq_system"],
                self.prompts["generate_faq_human"],
                self.prompts["generated_faq"],
                self.prompts["decrease_charactercount_human"],
            ]
        )
        runnable = prompt | llm | StrOutputParser()
        answer_character_count = len(info["faq"]["answer"].split(" "))
        if answer_character_count > 400:
            return RunnablePassthrough() | RunnablePassthrough.assign(faq=runnable)
        return info

    def format_faq_chain_output(self, output):
        formatted = []
        for faq in output:
            formatted.append(faq["faq"])
        return formatted

    def check_faq_similarity(self, faqs):
        corpus = [x["answer"] for x in faqs]
        text_comparer = TextComparer(corpus)
        groups_of_similar_answers_by_index = text_comparer.find_similar_groups()
        groups_of_similar_answers_by_contents = []
        for group in groups_of_similar_answers_by_index:
            group_with_text = [faqs[x] for x in group]
            groups_of_similar_answers_by_contents.append(group_with_text)
        return groups_of_similar_answers_by_contents

    def generate_faqs(self, inputs: List[dict], output_filepath: str = False):
        prompt = ChatPromptTemplate.from_messages(
            [self.prompts["generate_faq_system"], self.prompts["generate_faq_human"]]
        )
        generate_faq_runnable = prompt | llm | JsonOutputParser(pydantic_object=FAQ)
        generate_faq_chain = RunnablePassthrough.assign(faq=generate_faq_runnable)
        optimize_faq_length_chain = generate_faq_chain | RunnableLambda(
            self.decrease_answer_character_count
        )

        generated_faqs = self.format_faq_chain_output(optimize_faq_length_chain.batch(inputs))
        similar_faqs = self.check_faq_similarity(generated_faqs)
        output = {"faqs": generated_faqs, "similarly_worded_faqs": similar_faqs}

        if output_filepath:
            with open(output_filepath, "w") as outfile:
                json.dump(output, outfile, indent=6)

        return output

if __name__ == "__main__":
    pass
    # content_generator = ContentGenerator(HXSGBrand.HALLER)
    # # content_generator.generate_blog_posts([{"topic": "Can central heating be installed in my house that doesn't already have it?", "brand_service_pages": HXSGBrand.HALLER.brand_service_pages}], "app/data/test1.json")
    # input_formatter = InputFormatter()

    # input = input_formatter.get_faq_topics_from_spreadsheet(
    #     "Question/Topic", "app/data/HomeX - AI Project - Phase 1.xlsx"
    # )
    # content_generator.generate_faqs(input, "app/data/phase_1_faqs.json")
