import requests
from bs4 import BeautifulSoup
# noinspection PyPackageRequirements
from seleniumwire import webdriver

"""
This module handles the link extraction and searching for FASTANI.
"""


class FastAniSpider:
    """
    Class for extracting network logs and anime links
    """
    base_url = 'https://fastani.net/animes'

    # Default page=1, works for most case, NOT TESTED ENOUGH for other animes.
    anime_search_url = 'https://fastani.net/api/data?page={page_num}&animes=1&search={anime_name}&tags=&years='

    def __init__(self):
        """
        Initialized chrome webdriver
        :return:
        """
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()

    def request_headers(self):
        """
        Extracts headers with auth token and cookies for making requests.
        Only run this function at the start of session to extract headers,
        make requests using 'requests' library.
        :return: dict(headers)
        """
        headers = None
        try:
            self.driver.get(self.base_url)

            auth_token_request_url = 'https://fastani.net/api/data/@me'
            self.driver.wait_for_request(path=auth_token_request_url, timeout=10)
        except Exception as e:
            print(e)
            print('Something went wrong when xtracting headers ...')
        else:
            headers = {'authority': 'fastani.net'}
            temp_headers = [req.headers for req in self.driver.requests if req.url == auth_token_request_url]
            # to remove single element nested list and convert tuple to dict
            headers.update(dict(temp_headers[0]))
            headers.update({'dnt': '1'})
            headers.pop('Host')
        finally:
            self.driver.close()
            # TODO: FOR TESTING
            print('Driver closed ...')

        return headers
    

if __name__ == '__main__':
    print(FastAniSpider().request_headers())
