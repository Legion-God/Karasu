import requests
from bs4 import BeautifulSoup
import itertools

'''
Gogoanime url = "https://gogoanime.sh/"
'''


class GogoAnimeSpider:
    """
    Handles searching and link extraction for Gogoanime.
    """
    base_url = 'https://gogoanime.sh/'

    def __init__(self, anime_page_url):
        self.anime_page_url = anime_page_url
    # TODO: think about refactoring the static methods to normal class methods

    @staticmethod
    def gogo_search(anime):
        """
        Returns the anime search results for the *anime*, with metadata.
        :param anime: str: anime to be searched
        :return: list of dicts containing anime metadata.
        """
        url = f'https://gogoanime.sh//search.html?keyword={anime}'
        search_resp = requests.get(url)
        soup = BeautifulSoup(search_resp.text, 'html.parser')
        list_soup = soup.find_all('ul', class_='items')
        list_soup = list_soup[0]
        item_soup = list_soup.find_all('p', class_='name')
        year_soup = list_soup.find_all('p', class_='released')

        # Stores search results in list of dicts
        anime_results = []

        for item, year_item in itertools.zip_longest(item_soup, year_soup):
            link = item.contents[0]['href']
            link = GogoAnimeSpider.base_url + link
            title = item.contents[0]['title']
            year = year_item.get_text(strip=True)
            # TODO: remove this in production
            print(f'Title: {title} Link: {link} Year: {year}')
            anime_results.append({'link': link, 'title': title, 'year': year})

        return anime_results

    @staticmethod
    def gogo_anime_supermeta_data(anime_url):
        """
        returns the meta data about anime
        :param anime_url: str: anime page url
        :return: dict containing meta data
        """
        resp = requests.get(anime_url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        div_soup = soup.find('div', class_='anime_info_body_bg')

        title = div_soup.h1.get_text(strip=True)
        meta_list = div_soup.find_all('p', class_='type')
        season_type = meta_list[0].get_text(strip=True)
        plot = meta_list[1].get_text(strip=True)
        genres = meta_list[2].get_text(strip=True)
        status = meta_list[4].get_text(strip=True)

        return {'title': title, 'season_type': season_type,
                'plot': plot, 'genres': genres, 'status': status}


if __name__ == '__main__':
    gogo_anime_url = GogoAnimeSpider.gogo_search('Naruto')[0]['link']
    print(GogoAnimeSpider.gogo_anime_supermeta_data(gogo_anime_url))
