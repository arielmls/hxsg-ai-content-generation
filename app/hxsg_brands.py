from enum import Enum
import json
import os


def load_service_pages():
    file_path = "app/data/service_pages.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}


class HXSGBrand(Enum):
    GEM = "Gem Plumbing and Heating"
    HALLER = "Haller Enterprises"
    UNIVERSE = "Universe Home Services"

    @property
    def brand_service_pages(self):
        all_brand_service_pages = load_service_pages()
        return all_brand_service_pages.get(self.value, {})
