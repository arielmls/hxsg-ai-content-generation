from typing import List
import pandas as pd
import json

from .hxsg_brands import HXSGBrand

class InputFormatter:
    def format_inputs(self, inputs: List[str], brand: HXSGBrand = HXSGBrand.HALLER):
        formatted = []
        for input in inputs:
            formatted_input = {
                "topic": input,
                "brand": brand.value,
                "brand_service_pages": brand.brand_service_pages,
            }
            formatted.append(formatted_input)
        return formatted

    def get_blog_post_topics_from_spreadsheet(
        self, topic_column_name, spreadsheet_filepath
    ):
        input_df = pd.read_excel(spreadsheet_filepath)
        if "Blog or FAQ" in input_df.columns:
            input_df = input_df[input_df["Blog or FAQ"] == "Blog"]
        input_df = input_df.rename(columns={topic_column_name: "topic"})
        inputs = self.format_inputs(
            json.loads(input_df["topic"].to_json(orient="records"))
        )
        return inputs

    def get_faq_topics_from_spreadsheet(self, topic_column_name, spreadsheet_filepath):
        input_df = pd.read_excel(spreadsheet_filepath)
        if "Blog or FAQ" in input_df.columns:
            input_df = input_df[input_df["Blog or FAQ"] == "FAQ"]
        input_df = input_df.rename(columns={topic_column_name: "topic"})
        inputs = self.format_inputs(
            json.loads(input_df["topic"].to_json(orient="records"))
        )
        return inputs
