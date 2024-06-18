from typing import List
import pandas as pd
import json

from .hxsg_brands import HXSGBrand, ServicePages


class InputFormatter:
    def format_inputs(self, inputs: List[str], service_pages: ServicePages, brand):
        formatted = []
        for input in inputs:
            formatted_input = {
                "topic": input,
                "brand": brand.value,
                "brand_service_pages": service_pages.get_service_page_descriptions(
                    brand
                ),
            }
            formatted.append(formatted_input)
        return formatted

    def get_topics_from_spreadsheet(
        self, topic_column_name, spreadsheet_filepath, content_type="FAQ"
    ):
        input_df = pd.read_excel(spreadsheet_filepath)
        if "Blog or FAQ" in input_df.columns:
            input_df = input_df[input_df["Blog or FAQ"] == content_type]
        input_df = input_df.rename(columns={topic_column_name: "topic"})
        inputs = self.format_inputs(
            json.loads(input_df["topic"].to_json(orient="records"))
        )
        return inputs
