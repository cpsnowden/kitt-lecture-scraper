import os

import requests
from bs4 import BeautifulSoup
from typing import Generator
from kitt.model import Lecture
from kitt.kitt_chrome import KittChrome


class KittLectureScraper:
    kitt_base_url = 'https://kitt.lewagon.com'

    def __init__(self, camp, auth_cookie_name, auth_cookie_value):
        """
        :param camp: the LeWagon camp number
        :param auth_cookie: a tuple containing the auth cookie (cookie_name, cookie_value)
        """
        self.camp = camp
        self.auth_cookie_name = auth_cookie_name
        self.auth_cookie_value = auth_cookie_value
        self.auth_cookie_dict = {auth_cookie_name: auth_cookie_value}

    def get_request_as_text(self, url: str) -> str:
        response = requests.get(url, cookies=self.auth_cookie_dict)
        response.raise_for_status()
        return response.text

    def get_lectures(self) -> Generator[Lecture, None, None]:
        html = self.get_request_as_text(self.resolve_url(f'camps/{self.camp}/lectures'))
        bs = BeautifulSoup(html, 'html.parser')
        for week in bs.find_all(class_='lecture-week-container'):
            week_title = week.find(class_='week-title').text
            for lecture_card_html in week.find_all(class_='lecture-list-card'):
                lecture = self.parse_lecture_card(week_title, lecture_card_html)
                yield lecture

    def get_lecture_content_link(self, lecture_url: str) -> str:
        response = self.get_request_as_text(lecture_url)
        bs = BeautifulSoup(response, 'html.parser')
        lecture_iframe = bs.find('iframe', {'id': 'karr_source_0'})
        return lecture_iframe.attrs['src'] if lecture_iframe else None

    def resolve_url(self, path):
        return f'{self.kitt_base_url}/{path}'

    def parse_lecture_card(self, week_title: str, lecture_bs: BeautifulSoup) -> Lecture:
        title = lecture_bs.find(class_='lecture-title').text.strip()

        print(f'Processing lecture: {title}')

        # Get Lecture page url
        lecture_path = lecture_bs.find(class_='lecture-card-link').get('href').strip('/')
        lecture_url = self.resolve_url(lecture_path)

        # Get HTML content url
        lecture_content_path = self.get_lecture_content_link(lecture_url)
        lecture_content_url = self.resolve_url(lecture_content_path)

        lecture = Lecture(week_title, title, lecture_url, lecture_content_url)
        print(f'Parsed lecture: {lecture}')

        return lecture

    def save_lecture_content_pdf(self, directory):
        kitt_chrome = KittChrome(self.kitt_base_url)
        kitt_chrome.login(self.auth_cookie_name, self.auth_cookie_value)
        for lecture in self.get_lectures():
            if lecture.content_url:
                file_name = lecture.content_url.split('/')[-1].replace('html', 'pdf')
                print(f"Saving {lecture.name} to pdf {file_name}")
                with open(os.path.join(directory, file_name), 'wb') as f:
                    f.write(kitt_chrome.print_page_to_pdf(lecture.content_url))
