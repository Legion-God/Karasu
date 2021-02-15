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

    def __init__(self):
        ...

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
    def gogo_anime_supermeta_data(anime_page_url):
        """
        returns the meta data about anime
        :param anime_page_url: str: anime page url
        :return: dict containing meta data
        """
        resp = requests.get(anime_page_url)
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
    def gogo_xtract_all_episodes_subpage_links(anime_page_url):
        """
        Extracts all the subpage episode links
        :param anime_page_url: str: anime page url, extracted from search function
        :return: episode_list: list of str: list of subpage urls, which points to video player links
        """
        sub_response = requests.get(anime_page_url)
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

        return episode_list

    @staticmethod
    def gogo_xtract_video_cdn_links(anime_subpage_url):
        """
        Extracts the link of download page from anime subpage.
        :param anime_subpage_url: str: episode sub page link
        :return: str: episode download page link
        """
        sub_page_response = requests.get(anime_subpage_url)
        sub_page_soup = BeautifulSoup(sub_page_response.text, 'html.parser')

        dwnload_page_link = sub_page_soup.find('li', class_='dowloads').a['href']
        return dwnload_page_link

    @staticmethod
    def gogo_xtract_direct_dwn_link(anime_cdn_url):
        cdn_page_response = requests.get(anime_cdn_url)
        cdn_soup = BeautifulSoup(cdn_page_response.text, 'html.parser')
        cdn_soup = cdn_soup.find_all('div', class_='mirror_link')
        download_urls = cdn_soup[0].find_all('a')
        alter_download_urls = cdn_soup[1].find_all('a')

        """A short function to clean the video resolution version of first list of download urls."""
        def clean_quality(quality_name): return quality_name.strip().split()[1][1:]

        # TODO: These download url requires special headers
        download_urls = [{clean_quality(url_item.get_text()): url_item['href']} for url_item in download_urls]

        """A short function to clean the video resolution of MIRROR download urls."""
        def clean_mirror(mirror_quality): return ''.join(mirror_quality.split()[1:])

        alter_download_urls = [{clean_mirror(url_item.get_text()): url_item['href']}
                               for url_item in alter_download_urls]

        def is_valid_url(mirror_url):
            """
            A function used for filtering the invalid urls provided by a group of providers.
            :param mirror_url: str: mirror download url
            :return:
            """
            invalid_providers = ['MixdropSV', 'mp4upload']
            for mirror_key, mirror_value in mirror_url.items():
                if mirror_key not in invalid_providers:
                    return mirror_url

        # Removes invalid providers
        alter_download_urls = list(filter(is_valid_url, alter_download_urls))

        print(download_urls)
        for i in alter_download_urls:
            print(i)

        print(len(alter_download_urls))


if __name__ == '__main__':
    gogo_anime_link = GogoAnimeSpider.gogo_search('Dororo')[0]['link']
    subpage_link = GogoAnimeSpider.gogo_xtract_all_episodes_subpage_links(gogo_anime_link)[8]
    cdn_page_link = GogoAnimeSpider.gogo_xtract_video_cdn_links(subpage_link)
    GogoAnimeSpider.gogo_xtract_direct_dwn_link(cdn_page_link)
