from dataclasses import dataclass


@dataclass
class Lecture:
    week: str
    name: str
    lecture_path: str
    lecture_content_path: str
