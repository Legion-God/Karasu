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
            # print(f'Title: {title} Link: {link} Year: {year}')
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

    @staticmethod
    def gogo_xtract_all_episodes_subpage_links(anime_url):
        """
        Extracts all the subpage episode links
        :param anime_url: str: anime page url, extracted from search function
        :return: list of str: list of subpage urls, which points to video player links
        """
        sub_response = requests.get(anime_url)
        soup = BeautifulSoup(sub_response.text, 'html.parser')

        # Extracts the first and last episode number
        episode_range_soup = soup.find('ul', id='episode_page').contents[1::2]

        ep_start = episode_range_soup[0].a['ep_start']
        ep_end = episode_range_soup[-1].a['ep_end']

        anime_id = soup.select('input#movie_id')[0]['value']
        default_ep = soup.select('input#default_ep')[0]['value']
        alias = soup.select('input#alias_anime')[0]['value']

        load_episode_list_url = f'https://ajax.gogocdn.net/ajax/load-list-episode?ep_start={ep_start}&ep_end={ep_end}' \
                                f'&id={anime_id}&default_ep={default_ep}&alias={alias}'

        episode_list_response = requests.get(load_episode_list_url)
        list_soup = BeautifulSoup(episode_list_response.text, 'html.parser')
        episode_list = list_soup.find('ul', id='episode_related')
        episode_list = episode_list.find_all('a')

        episode_list = [GogoAnimeSpider.base_url + episode_item['href'].lstrip()
                        for episode_item in reversed(episode_list)]
        print(episode_list)


if __name__ == '__main__':
    gogo_anime_url = GogoAnimeSpider.gogo_search('Naruto')[0]['link']
    GogoAnimeSpider.gogo_xtract_all_episodes_subpage_links(gogo_anime_url)
