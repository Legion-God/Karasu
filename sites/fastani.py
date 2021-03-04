import requests
# noinspection PyPackageRequirements
from seleniumwire import webdriver
from collections import namedtuple
from datetime import date
import json

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

    def fast_ani_full_data_json(self, anime, headers, page=1):
        """
        Returns a list of JSON with metadata and episode direct url.
        :param anime: str: anime name to be search
        :param headers: dict: a dictionary that contains cookies, auth headers and other usual stuff.
        :param page: int: anime results page number
        :return: list of JSON: list of anime search results JSON responses.
        """
        search_url = self.anime_search_url.format(page_num=page, anime_name=anime)
        resp = requests.get(search_url, headers=headers)
        dict_response = resp.json()
        # Removes reviews from response.
        dict_response['animeData']['cards'][0].pop('reviews', None)
        return dict_response

    @staticmethod
    def fast_ani_search_results(anime_response):
        """
        Returns a namedTuple response by extracting anime search results with title and date info.
        :param anime_response: dict: takes full data JSON response returned from fast_ani_full_data_json
        :return: namedTuple: returns title, start date, season number, total episodes.
        """

        ShowSeason = namedtuple('ShowSeason', ['season_number', 'num_episodes'])
        SearchResult = namedtuple('SResults', ['title', 'romaji_title', 'start_date', 'season'])
        anime_results = anime_response['animeData']['cards']
        results_list = []

        for result in anime_results:
            # Stores season number with total episodes that season in namedtuple.
            show_season_list = []

            for season_number, all_seasons_list in enumerate(result['cdnData']['seasons'], 1):
                show_season_list.append(
                    ShowSeason(season_number=season_number, num_episodes=len(all_seasons_list['episodes'])))

            # Lambda function converts date to std format.
            results_list.append(SearchResult(title=result['title']['english'],
                                             romaji_title=result['title']['romaji'],
                                             start_date=(lambda date_info: date(year=date_info['year'],
                                                                                month=date_info['month'],
                                                                                day=date_info['day']).strftime('%D'))(
                                                 result['startDate']),
                                             season=show_season_list
                                             ))
        return results_list


if __name__ == '__main__':
    fast_ani = FastAniSpider()
    auth_headers = fast_ani.request_headers()
    response = fast_ani.fast_ani_full_data_json(anime='Boku No Hero Academia', headers=auth_headers)
    # print(json.dumps(response, indent=4))
    results = fast_ani.fast_ani_search_results(response)
    print(results)
