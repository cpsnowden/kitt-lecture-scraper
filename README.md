# kitt-lecture-scraper

This is a simple tool to enable bulk saving of all lecture notes from LeWagon's Kitt platform to PDF

The following shows how to run the scraper for your:
1. camp_id: this is your camp number
2. cookie_value: you can get this cookie after logging into kitt and checking your browser cookies

```python
from kitt.scraper import KittLectureScraper

camp_id = <YOUR_CAMP_ID>
cookie_name = '_kitt2017_'
cookie_value = <INSERT YOUR COOKIE HERE>
save_directory = 'lectures'

scraper = KittLectureScraper(camp_id, cookie_name, cookie_value)
scraper.save_lecture_content_pdf(save_directory)
```

or run via command line

```commandline
python kitt/scraper.py -c <camp_number> --cookie_name=<cookie_name> --cookie_value=<cookie_value> -o <save_directory>
```