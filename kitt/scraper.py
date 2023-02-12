import requests
import os
import base64
from bs4 import BeautifulSoup
from kitt.model import Lecture
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.print_page_options import PrintOptions


class KittLectureScraper:
    kitt_base_url = 'https://kitt.lewagon.com'

    def __init__(self, camp, auth_cookie):
        """
        :param camp: the LeWagon camp number
        :param auth_cookie: a tuple containing the auth cookie (cookie_name, cookie_value)
        """
        self.camp = camp
        self.camp_url = f'{self.kitt_base_url}/camps/{camp}'
        self.auth_cookie_kv = auth_cookie
        self.auth_cookie = {auth_cookie[0]: auth_cookie[1]}

    def get_lectures_html(self) -> str:
        response = requests.get(f'{self.camp_url}/lectures', cookies=self.auth_cookie)
        response.raise_for_status()
        return response.text

    def get_lectures(self) -> list[Lecture]:
        html = self.get_lectures_html()
        bs = BeautifulSoup(html, 'html.parser')

        lectures = []
        for week in bs.find_all(class_='lecture-week-container'):
            week_title = week.find(class_='week-title').text
            for lecture_card in week.find_all(class_='lecture-list-card'):
                lectures.append(self.parse_lecture_card(week_title, lecture_card))
        return lectures

    def get_lecture_content_link(self, lecture_path) -> str:
        response = requests.get(f'{self.kitt_base_url}/{lecture_path}', cookies=self.auth_cookie)
        response.raise_for_status()
        bs = BeautifulSoup(response.text, 'html.parser')
        lecture_iframe = bs.find('iframe', {'id': 'karr_source_0'})
        return lecture_iframe.attrs['src'] if lecture_iframe else None

    def parse_lecture_card(self, week_title: str, lecture_bs: BeautifulSoup) -> Lecture:
        title = lecture_bs.find(class_='lecture-title').text.strip()
        print(f'Processing HTML for {title}')
        lecture_path = lecture_bs.find(class_='lecture-card-link').get('href').strip('/')
        lecture_content_path = self.get_lecture_content_link(lecture_path)
        lecture = Lecture(week_title, title, lecture_path, lecture_content_path)
        print(f'Processed lecture {lecture}')
        return lecture

    def check_content(self, lecture: Lecture):
        if lecture.lecture_content_path:
            url = f'{self.kitt_base_url}/{lecture.lecture_content_path}'
            response = requests.get(url, cookies=self.auth_cookie)
            if (response.status_code == 404):
                print(f"Could not find lecture {lecture.name} at url: {url}")
            else:
                print(f"Found content for lecture {lecture.name}")
        else:
            print(f"Lecture {lecture.name} has no content")

    def save_lecture_content_html(self, directory):
        lectures = self.get_lectures()
        for lecture in lectures:
            if lecture.lecture_content_path:
                url = f'{self.kitt_base_url}/{lecture.lecture_content_path}'
                response = requests.get(url, cookies=self.auth_cookie)
                response.raise_for_status()
                file = os.path.join(directory, lecture.lecture_content_path.split('/')[-1])
                with open(file, "w") as f:
                    f.write(response.text)

    def save_lecture_content_pdf(self, directory):
        lectures = self.get_lectures()

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 15)
        driver.get("https://kitt.lewagon.com")
        driver.add_cookie({'name': self.auth_cookie_kv[0], 'value': self.auth_cookie_kv[1], 'domain': 'kitt.lewagon.com'})
        driver.get("https://kitt.lewagon.com/camps/1133/lectures")

        for lecture in lectures:
            if lecture.lecture_content_path:
                print(f"Saving {lecture.name} to pdf")
                url = f'{self.kitt_base_url}/{lecture.lecture_content_path}'
                driver.get(url)
                wait.until(ec.visibility_of_element_located((By.XPATH, "//div[@id='notebook-container']")))

                content = driver.print_page(PrintOptions())
                file = os.path.join(directory, lecture.lecture_content_path.split('/')[-1]).replace('html', 'pdf')
                with open(file, 'wb') as f:
                    f.write(base64.b64decode(content))