import base64
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

    def print_page_to_pdf(self, link):
        self.driver.get(link)
        content = self.driver.print_page(PrintOptions())
        return base64.b64decode(content)
