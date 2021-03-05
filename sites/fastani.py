import requests
# noinspection PyPackageRequirements
from seleniumwire import webdriver
from collections import namedtuple
from datetime import date
import json
import re

"""
This module handles the link extraction and searching for FASTANI.
"""


def show_date(date_dict):
    """
    A utility function to convert a date dict to std format, returns str
    :param date_dict: dict: containing day, month, year
    :return: str: DD/MM/YYYY
    """
    date_format = '%d/%m/%Y'
    return date(year=date_dict['year'], month=date_dict['month'], day=date_dict['day']).strftime(date_format)


def clean_string(raw_string):
    """
    A utility function to remove html elements from a string.
    :param raw_string: str: pass the unclean string with html tags
    :return: str: clean string with no html tags
    """
    html_cleaner_regex = re.compile(r'<.*?>')
    return html_cleaner_regex.sub('', raw_string).strip()


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
    def fast_ani_season_results(anime_card_cdn_data):
        """
        Xtracts the number of seasons and total episode in single anime
        :param anime_card_cdn_data: cdnData of single card list item
        :return: list of ShowSeason(season_number, num_episodes)
        """
        show_season_list = []
        ShowSeason = namedtuple('ShowSeason', ['season_number', 'num_episodes'])

        for season_number, season in enumerate(anime_card_cdn_data['seasons'], 1):
            show_season_list.append(
                ShowSeason(season_number=season_number, num_episodes=len(season['episodes'])))
        return show_season_list

    def fast_ani_search_results(self, anime_response):
        """
        Returns a namedTuple response by extracting anime search results with title and date info.
        :param anime_response: dict: takes full data JSON response returned from fast_ani_full_data_json
        :return: namedTuple: returns title, start date, season number, total episodes.
        """

        SearchResult = namedtuple('SResults', ['title', 'romaji_title', 'start_date', 'season'])
        anime_results = anime_response['animeData']['cards']
        results_list = []

        for result in anime_results:
            results_list.append(SearchResult(title=result['title']['english'],
                                             romaji_title=result['title']['romaji'],
                                             start_date=show_date(result['startDate']),
                                             season=self.fast_ani_season_results(result['cdnData'])))
        return results_list

    '''control flow for the anime search results and link extraction from the JSON response. Show the anime search 
    results to the user in FastAni way, seasons are aggregated under same Anime name. then user is given choice to 
    choose the anime, after which seasons are revealed with metadata(description, tags, and season information). 
    choose the season to download with an option.
    
    so, create a function to extract metadata about a anime, this will triggered ONLY if the user has chosen that 
    anime and after printing meta data about anime, show the season information.
    '''

    # FIXME: make anime response a property of the class.
    # FIXME: make it's inner data also a property of the class.
    @staticmethod
    def fast_ani_anime_metadata(anime_card_response):
        """
        Xtracts the description, genres, startDate, title
        :param anime_card_response: anime item from card list (a single item with 0+ Seasons)
        :return: namedtuple: Metadata(descrip, genres, startDate, title, romaji_title)
        """
        Metadata = namedtuple('Metadata', ['descrip', 'genres', 'start_date', 'title', 'romaji_title'])
        return Metadata(descrip=clean_string(anime_card_response['description']), genres=anime_card_response['genres'],
                        start_date=show_date(anime_card_response['startDate']),
                        title=anime_card_response['title']['english'],
                        romaji_title=anime_card_response['title']['romaji'])

    def fast_ani_episode_links(self, anime_response, season_num, epi_start, epi_end):
        """
        Returns a list of namedtuple with episode link and filename for specified params
        :param anime_response: selected anime dict response from list of card items.
        :param season_num: season number of anime
        :param epi_start: start episode to download
        :param epi_end: ending episode to download
        :return: list(namedtuple(['url', 'filename']))
        """
        # TODO: Convert season number to 0 based system before passing to function.
        DownLink = namedtuple('DownLink', ['epi_url', 'filename'])
        season_list_response = anime_response['cdnData']['seasons'][season_num]['episodes'][epi_start:epi_end]
        return [DownLink(epi_url=episode['file'],
                         filename=(lambda url: url.split('/')[-1])(episode['file']))
                for episode in season_list_response]


if __name__ == '__main__':
    fast_ani = FastAniSpider()
    auth_headers = fast_ani.request_headers()
    response = fast_ani.fast_ani_full_data_json(anime='Boku No Hero Academia', headers=auth_headers)
    # print(json.dumps(response, indent=4))
    results = fast_ani.fast_ani_search_results(response)
    # print(results)
    # print(fast_ani.fast_ani_anime_metadata(response['animeData']['cards'][0]))
    print(fast_ani.fast_ani_episode_links(anime_response=response['animeData']['cards'][0],
                                          season_num=1, epi_start=0, epi_end=8))
