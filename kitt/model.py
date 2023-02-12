from dataclasses import dataclass


@dataclass
class Lecture:
    week: str
    name: str

    home_page_url: str
    content_url: str
