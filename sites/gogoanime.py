import requests
from bs4 import BeautifulSoup
import itertools
import json
from collections import namedtuple

'''
Gogoanime url = "https://www2.gogoanime.sh/"
'''

"""
Some utility functions for extracting mirror links from providers.
"""


# TODO: Implement extractor for dood.to provider
# FIXME: change the dictionary and tuples to namedtuples wherever possible


def stream_sb(provider_url):
    """
    Extracts direct download links from indirect video provider links
    :param provider_url: indirect video provider link.
    :return: dict: dict multiple quality direct downlaod links.
    """
    # FIXME: stream_sb probably uses requests rate limiting, check this later.
    # base url for the stream_sb video
    stream_sb_base_url = 'https://streamsb.net/dl?op=download_orig&'

    resp = requests.get(provider_url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    table_soup = soup.find_all('td')
    dwnload_360_soup = table_soup[0].a
    dwnload_360_info = table_soup[1].get_text(strip=True)

    dwnload_720_soup = table_soup[2].a
    dwnload_720_info = table_soup[3].get_text(strip=True)

    def xtract_stream_sb_params(string_with_params):
        """
        Returns string with params embedded extracted from another string.
        :param string_with_params: str: a string with params
        :return: str: a string with params embedded
        """
        params = string_with_params.split("'")
        id_episode = params[1]

        # download normal(mode=n) or high res(mode=h) quality video.
        quality_episode = params[3]
        hash_episode = params[5]
        return f'{stream_sb_base_url}id={id_episode}&mode={quality_episode}&hash={hash_episode}'

    def xtract_stream_direct_dwnload_url(download_page_url):
        """
        Extracts direct download link from download page
        :param download_page_url: str: download page url
        :return: str: direct download url
        """
        dwn_page_resp = requests.get(download_page_url)
        dwn_page_soup = BeautifulSoup(dwn_page_resp.text, 'html.parser')
        url = dwn_page_soup.find('div', class_='contentbox').span.a['href']
        return url

    download_360_url = xtract_stream_direct_dwnload_url(xtract_stream_sb_params(dwnload_360_soup['onclick']))
    download_720_url = xtract_stream_direct_dwnload_url(xtract_stream_sb_params(dwnload_720_soup['onclick']))

    def is_alive(video_url):
        """
        Returns True if a video is alive.
        :param video_url: video url
        :return: bool:
        """
        if requests.head(video_url).headers['Content-Type'] == 'text/html':
            return False
        else:
            return True

    if is_alive(download_360_url):
        if is_alive(download_720_url):
            return [{'is_alive': True}, {'360': download_360_url, 'meta_data': dwnload_360_info},
                    {'720': download_720_url, 'meta_data': dwnload_720_info}]
        else:
            return [{'is_alive': True}, {'360': download_360_url, 'meta_data': dwnload_360_info}]
    else:
        if is_alive(download_720_url):
            return [{'is_alive': True}, {'360': download_720_url, 'meta_data': dwnload_720_info}]
        else:
            return [{'is_alive': False}]


def xtream_cdn(provider_url):
    """
    Xtracts direct download link from Xtream video provider
    :param provider_url: str: takes indirect link to video page
    :return: returns direct download link
    """

    def is_down(provider_stream_url):
        """
        Checks if the video is been DMCAed.
        :param provider_stream_url: str: url for indirect video page
        :return: bool:
        """
        down_resp = requests.get(provider_stream_url)
        down_soup = BeautifulSoup(down_resp.text, 'html.parser')
        message = down_soup.p.get_text(strip=True)

        if 'DMCA Takedown' in message:
            return True
        else:
            return False

    if is_down(provider_url):
        print('DMCA Take down :( Try another servers ...')
        return [{'is_alive': False}]
    else:
        split_url = provider_url.split('/f/')
        post_url = f'{split_url[0]}/api/source/{split_url[1]}'

        xstream_resp = requests.post(post_url).text
        redirect_urls = json.loads(xstream_resp)['data']
        direct_urls = [{url_item['label']: requests.get(url_item['file'], stream=True).url}
                       for url_item in redirect_urls]
        direct_urls.insert(0, {'is_alive': True})
        return direct_urls


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

        # TODO: IMP: extract the episode title and save it with return list of results
        """A short function to clean the video resolution version of first list of download urls."""

        def clean_quality(quality_name):
            return quality_name.strip().split()[1][1:]

        # TODO: These download url requires special headers
        download_urls = [{clean_quality(url_item.get_text()): url_item['href']} for url_item in download_urls]

        """A short function to clean the video resolution of MIRROR download urls."""

        def clean_mirror(mirror_quality):
            return ''.join(mirror_quality.split()[1:])

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

        # FIXME: Integrate utility functions for alter_download_urls
        return {'links': download_urls, 'mirror_links': alter_download_urls}

    # TODO: create a namedtuple for categories for recent released.
    @staticmethod
    def gogo_recent_released(page_number=1, show_type=1):
        """
        Takes a named tuple indicating page number and show_type.
        :param page_number: int: page number of recent releases
        :param show_type: int describing type of show ['sub', 'dub', chinese], start_index=1
        :return: list(namedtuple(['show_title', 'episode', 'link']))
        """

        # Input validation for the params
        def recent_released_params_validation(page_val=page_number, type_val=show_type):
            """
            Validates if params are correct.
            :param page_val: int: page number of recent release
            :param type_val: int: type of show
            :return: bool: returns true if everything is correct else false.
            """

            if not 1 <= type_val <= 3:
                return False

            # Gives the last page number of certain type.
            val_recent_release_url = f'https://ajax.gogocdn.net/ajax/page-recent-release.html?page=999&type={type_val}'
            val_resp = requests.get(val_recent_release_url)
            val_soup = BeautifulSoup(val_resp.text, 'html.parser')
            val_last_page = val_soup.find('ul', class_='pagination-list').find_all('a')
            val_last_page = [int(val_page_item.get_text(strip=True)) for val_page_item in val_last_page]
            val_last_page = val_last_page[-1]

            if 1 <= page_val <= val_last_page:
                return True
            else:
                return False

        if recent_released_params_validation(page_number, show_type):
            # Input is correct, proceed further
            recent_release_url = f'https://ajax.gogocdn.net/ajax/page-recent-release.html?page={page_number}' \
                                 f'&type={show_type}'
            recent_release_resp = requests.get(recent_release_url)
            recent_release_soup = BeautifulSoup(recent_release_resp.text, 'html.parser')
            li_soup = recent_release_soup.find('ul', class_='items').contents

            # CLeans unwanted elements from show lists
            uncleaned_recent_released_shows = li_soup[1::2]

            Recent = namedtuple('Recent', ['show_name', 'episode', 'link'])

            recent_released_shows = list(map(lambda show: Recent(show_name=show.find('p', class_='name').a.get_text(),
                                                                 episode=show.find('p', class_='episode').get_text(),
                                                                 link=GogoAnimeSpider.base_url +
                                                                 show.find('p', class_='name').a['href']),
                                             uncleaned_recent_released_shows))
            return recent_released_shows

        else:
            print('Incorrect Input ...')
            # TODO: Write some logic for handling incorrect case.


if __name__ == '__main__':
    # gogo_anime_link = GogoAnimeSpider.gogo_search('Dororo')[0]['link']
    # subpage_link = GogoAnimeSpider.gogo_xtract_all_episodes_subpage_links(gogo_anime_link)[8]
    # cdn_page_link = GogoAnimeSpider.gogo_xtract_video_cdn_links(subpage_link)
    # download_links = GogoAnimeSpider.gogo_xtract_direct_dwn_link(cdn_page_link)
    #
    # print(json.dumps(download_links, indent=4))

    # stream_sb('https://streamsb.net/d/8axfbcx6xaon.html')
    # xtream_cdn('https://fcdn.stream/f/7z9-z5072ox')

    # TESTING for recent release list
    GogoAnimeSpider.gogo_recent_released()
