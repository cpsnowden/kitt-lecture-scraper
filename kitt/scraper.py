import os

import requests
from bs4 import BeautifulSoup
from typing import Generator
from kitt.model import Lecture
from kitt.kitt_chrome import KittChrome


class KittLectureScraper:
    kitt_base_url = 'https://kitt.lewagon.com'

    def __init__(self, camp_number, auth_cookie_name, auth_cookie_value):
        """
        :param camp_number: the LeWagon camp number
        :param auth_cookie_name: the name of the Kitt auth cookie (e.g. '_kitt2017_')
        :param auth_cookie_value: the value of the Kitt auth cookie
        """
        self.camp = camp_number
        self.auth_cookie_name = auth_cookie_name
        self.auth_cookie_value = auth_cookie_value
        self.auth_cookie_dict = {auth_cookie_name: auth_cookie_value}

    def __get_text(self, url: str) -> str:
        """
        Get the contents at the given url as text checking the response code

        :param url: the url request
        :raise HTTPError if an error occurs during the request
        :return: the text content of the response
        """
        response = requests.get(url, cookies=self.auth_cookie_dict)
        response.raise_for_status()
        return response.text

    def __get_lecture_content_url(self, lecture_url: str) -> str:
        """
        Retrieves the HTML content link by parsing the lecture home page for the embedded iframe

        :param lecture_url: the lecture home page
        :return: the url for the lecture notes, or None if it cannot be found on the page
        """
        response = self.__get_text(lecture_url)
        bs = BeautifulSoup(response, 'html.parser')
        lecture_iframe = bs.find('iframe', {'id': 'karr_source_0'})
        if lecture_iframe:
            return self.__resolve_url(lecture_iframe.attrs['src'])

    def __resolve_url(self, path):
        """
        Resolve the given relative path e.g. /foobar against the base kitt url

        :param path: the path to resolve
        :return: the resolved path
        """
        return f'{self.kitt_base_url}/{path}'

    def __parse_lecture_card(self, week_title: str, lecture_bs: BeautifulSoup) -> Lecture:
        title = lecture_bs.find(class_='lecture-title').text.strip()

        print(f'Processing lecture: {title}')

        # Get Lecture page url
        lecture_path = lecture_bs.find(class_='lecture-card-link').get('href').strip('/')
        lecture_url = self.__resolve_url(lecture_path)

        # Get HTML content url
        lecture_content_url = self.__get_lecture_content_url(lecture_url)

        lecture = Lecture(week_title, title, lecture_url, lecture_content_url)
        print(f'Parsed lecture: {lecture}')

        return lecture

    def get_lectures(self) -> Generator[Lecture, None, None]:
        """
        Get all the lecture metadata for a camp

        :return: a sequence of Lecture objects
        """
        html = self.__get_text(self.__resolve_url(f'camps/{self.camp}/lectures'))
        bs = BeautifulSoup(html, 'html.parser')
        for week in bs.find_all(class_='lecture-week-container'):
            week_title = week.find(class_='week-title').text
            for lecture_card_html in week.find_all(class_='lecture-list-card'):
                lecture = self.__parse_lecture_card(week_title, lecture_card_html)
                yield lecture

    def save_lecture_content(self, directory, file_type='pdf'):
        """
        Save all the lectures for the camp to a given directory. If the directory
        does not exist, then it will be created

        :param file_type: the format of file to save, defaults to pdf
        :param directory: the directory to save to
        """
        os.makedirs(directory, exist_ok=True)

        kitt_chrome = KittChrome(self.kitt_base_url)
        kitt_chrome.login(self.auth_cookie_name, self.auth_cookie_value)
        for lecture in self.get_lectures():
            if lecture.content_url:
                file_name = lecture.content_url.split('/')[-1].rstrip('.html')
                path = os.path.join(directory, file_name)
                kitt_chrome.print_page_as_format(path, lecture.content_url, file_type=file_type)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        prog='Kitt Lecture Scraper'
    )
    parser.add_argument('-c', '--camp', type=int, help='LeWagon camp number', required=True)
    parser.add_argument('-o', '--out', help='Target directory', required=True)
    parser.add_argument('--cookie_name', help='LeWagon Cookie Name', required=True)
    parser.add_argument('--cookie_value', help='LeWagon COokie Value', required=True)

    args = parser.parse_args()
    scraper = KittLectureScraper(args.camp, args.cookie_name, args.cookie_value)
    scraper.save_lecture_content(args.out, file_type='pdf')
