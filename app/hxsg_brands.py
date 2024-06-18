from enum import Enum
import json
import os
import requests
import logging
from typing import List
from fastapi import HTTPException


class HXSGBrand(Enum):
    GEM = "Gem Plumbing and Heating"
    HALLER = "Haller Enterprises"
    UNIVERSE = "Universe Home Services"


class WordpressPageAccessor:
    def __init__(self) -> None:
        pass

    def wordpress_pages_request(self, wordpress_pages_url, perpage, page):
        try:
            res = requests.get(f"{wordpress_pages_url}?page={page}&per_page={perpage}")
        except Exception as e:
            logging.error(
                f"Error:  Could not access wordpress_pages at url {wordpress_pages_url}\n {e}"
            )
            raise HTTPException(500, detail=e)
        else:
            return res

    def wordpress_pagination(self, wordpress_pages_url, perpage=100):
        all_pages = []
        current_page = 1
        first_response = self.wordpress_pages_request(
            wordpress_pages_url, perpage, page=current_page
        )
        total_pages = int(first_response.headers["X-WP-TotalPages"])
        all_pages.extend(first_response.json())

        while current_page < total_pages:
            current_page += 1
            all_pages.extend(
                self.wordpress_pages_request(
                    wordpress_pages_url, perpage, current_page
                ).json()
            )

        return all_pages

    def get_service_pages_descriptions(
        self, categories: List[str], wordpress_pages: dict
    ) -> dict:
        page_details = {}
        for i, page in enumerate(wordpress_pages):
            for category in categories:
                try:
                    link = page["link"]
                except:
                    raise Exception(f"page: {i}")
                if link.startswith(category):
                    page_details[link] = {
                        "title": page["title"]["rendered"],
                        "excerpt": page["excerpt"]["rendered"],
                    }
        return page_details

    def access_service_page_descriptions(self, wordpress_info):
        service_pages_details = {}
        for brand in wordpress_info.keys():
            wordpress_pages = self.wordpress_pagination(
                wordpress_info[brand]["wordpress_pages_url"]
            )
            page_details = self.get_service_pages_descriptions(
                wordpress_info[brand]["service_categories"], wordpress_pages
            )
            service_pages_details[brand] = page_details
        return service_pages_details


class ServicePages:
    def __init__(
        self, wordpress_info, wordpress_page_accessor: WordpressPageAccessor
    ) -> None:
        self.all_page_descriptions = wordpress_page_accessor.access_service_page_descriptions(
            wordpress_info
        )

    def get_service_page_descriptions(
        self, brand: HXSGBrand = None
    ) -> dict[dict[str, str]]:
        if brand is None:
            return self.all_page_descriptions
        return self.all_page_descriptions.get(brand.value, {})
