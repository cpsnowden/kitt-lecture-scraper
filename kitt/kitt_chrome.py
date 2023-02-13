import base64
import os.path
from urllib.parse import urlparse

from selenium.webdriver import ChromeOptions, Chrome
from selenium.webdriver.common.print_page_options import PrintOptions


class KittChrome:
    """
        Wrapper around selenium used to save Kitt pages as PDF, if produced the nicest format vs pdfkit
    """

    def __init__(self, root_url):
        options = ChromeOptions()
        options.add_argument("--headless")
        self.root_url = root_url
        self.domain = urlparse(root_url).netloc
        self.driver = Chrome(options=options)
        self.driver.get(root_url)

    def login(self, cookie_name, cookie_value):
        self.driver.add_cookie({'name': cookie_name, 'value': cookie_value, 'domain': self.domain})
        # Trigger refresh
        self.driver.get(self.root_url)

    def print_page_as_format(self, path, link, file_type='pdf'):
        self.driver.get(link)
        print(f"Saving {link} to {path}")
        if file_type == 'pdf':
            self.__print_page_as_pdf(path)
        else:
            raise ValueError(f'Unsupported format {file_type}')

    def __print_page_as_pdf(self, path):
        content = self.driver.print_page(PrintOptions())
        with open(path + '.pdf', 'wb') as f:
            f.write(base64.b64decode(content))
