from selenium import webdriver
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import re
from webdrivermanager import ChromeDriverManager

'''
Supported Anime Sites.
chia_anime_url = 'http://www.chia-anime.me/'
'''


# ChromeDriverManager().download_and_install()
# TODO: make this class property with user option to download and install webdriver.
# TODO: refactor the class to represent the anime

class ChiaAnimeSpider:
    """
    Class for extracting and downloading anime episodes.
    """

    def __init__(self, chia_anime_page_url):
        """
        Prepares the object for crawling.
        :param chia_anime_page_url: pass the anime page url of chia anime.
        """

        self.anime_page_url = chia_anime_page_url
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

    @staticmethod
    def chia_anime_supermeta_data(anime_url):
        """
        Extracts the anime total episode and genres and returns them as dict.
        :return: anime super meta data dict.
        """
        anime_page_response = requests.get(anime_url).text
        soup = BeautifulSoup(anime_page_response, 'html.parser')
        div_soup = soup.find_all('blockquote')
        div_soup = div_soup[:-1]

        title_list, meta_list = div_soup
        title_list = title_list.contents[1::2]
        meta_list = meta_list.contents[1::2]

        # Title data
        english_title = title_list[0].get_text(strip=True)
        alter_title = title_list[1].get_text(strip=True)

        # Meta data
        total_episodes = meta_list[1].get_text(strip=True)
        status = meta_list[2].get_text(strip=True)
        aired = meta_list[3].get_text(strip=True)
        genres = meta_list[5].get_text(strip=True)
        rating = meta_list[7].get_text(strip=True)

        return {'english_title': english_title, 'alter_title': alter_title,
                'total_episodes': total_episodes, 'status': status, 'aired': aired,
                'genres': genres, 'rating': rating}

    @staticmethod
    def find_epi_num_in_title(page_title):
        """
        Helper function to extract the episode number from the page title using regex and returns epi_number
        :param page_title: page title of the anime video player
        :return: string with epi_number
        """
        epi_number_regex = re.compile('Episode ([0-9]+)')
        return epi_number_regex.findall(page_title)[0]

    def chia_xtract_all_episodes_subpage_links(self):
        """
        Extracts ALL the episode SUBPAGE links from the anime page and stores them in list.
        :return: list of episode page links
        """
        anime_page_response = requests.get(self.anime_page_url).text
        # div class="post"  > a href=Target url
        main_page_soup = BeautifulSoup(anime_page_response, 'html.parser')
        div_posts_soup = main_page_soup.find_all('div', class_='post')

        # Removes the first element which has garbage data.
        div_sliced_post_soup = div_posts_soup[1:]

        # Store all the subpage episode links.
        sub_page_links = [div_soup.a['href'] for div_soup in reversed(div_sliced_post_soup)]

        # TODO: Delete this in production.
        # for episode, link in enumerate(sub_page_links, 1):
        #     print(f'Episode:{episode} link:{link}')

        return sub_page_links

    @staticmethod
    def xtract_video_links(epi_subpage_links):
        """
        Extracts cdn links from the list slice of subpage links.
        :param epi_subpage_links: slice of list of episode page links.
        :return: returns a list of downloadable video links.
        """

        cdn_links = []

        for sublink in epi_subpage_links:
            subpage_response = requests.get(sublink).text
            subpage_soup = BeautifulSoup(subpage_response, 'html.parser')

            # Extracts the link for KM player
            video_player_div_soup = subpage_soup.find('div', class_='play-video selected')

            cdn_link = video_player_div_soup.contents[1]['src']
            cdn_links.append(cdn_link)

        return cdn_links

    def xtract_dwnload_links(self, epi_cdn_links):
        """
        Creates the list of extracted direct download video links
        :param epi_cdn_links: pass the list of cdn_links extracted from the xtract_video_link()
        :return: returns the list of direct download video links
        """

        direct_dwnload_links = [self.xtract_player_selenium(episode) for episode in epi_cdn_links]

        # Close the browser after extracting all the direct dwn links.
        self.driver.quit()
        return direct_dwnload_links

    def xtract_player_selenium(self, player_cdn_link):
        """
        returns a direct download video from a given cdn link
        :param player_cdn_link: single cdn link.
        :return: tuple with download link and file name for the video file.
        """

        # Extract this element 'src' after clicking on the video player
        # //body/div[1]/div[1]/div[1]/div[2]/video[1]
        # TODO: keep clearing cookies when making request to cdn link to fetch direct download link.
        self.driver.get(player_cdn_link)
        vid_title = self.driver.title
        print(f'Scraping {vid_title}')

        # TODO: testing a better way
        js_anime_360 = 'return se2'
        js_anime_720 = 'return se'
        anime_source_360 = self.driver.execute_script(js_anime_360)
        anime_source_720 = self.driver.execute_script(js_anime_720)

        anime_source_360 = anime_source_360.replace('\x00', '')
        anime_source_720 = anime_source_720.replace('\x00', '')

        vid_dwn_link = {'360': anime_source_360, '720': anime_source_720}

        print(f'Done {vid_title}')
        return vid_dwn_link, vid_title

    @staticmethod
    def chia_search(anime):
        """
        Returns the anime search results for the *anime*, which contains anime links.
        :param anime: str , anime to be searched.
        :return: list of dicts containing anime metadata.
        """
        base_url = f'http://www.chia-anime.me/mysearch.php?nocache&s=&search={anime}'

        search_response = requests.get(base_url)
        search_soup = BeautifulSoup(search_response.text, 'html.parser')
        div_soup = search_soup.select('div[style="margin-left: 50px !important;padding-top:-10px !important;"]')

        anime_results = []

        # Extracts the metadata from each individual anime and stores them as dict in the list.
        for meta_anime in div_soup:
            link = meta_anime.a['href']
            title = meta_anime.a.string

            # next sibling after 'a' tag is '\n', episode div appears after '\n'
            temp_episode_element = meta_anime.a.next_sibling.next_sibling
            episode = temp_episode_element.string

            # next sibling after 'a' tag is '\n', year div appears after '\n'
            year = temp_episode_element.next_sibling.next_sibling.string
            anime_results.append({'link': link, 'title': title, 'episodes': episode, 'year': year})

        return anime_results


# Testing

if __name__ == '__main__':
    # TODO: VAR: anime_page_url
    arg_anime_page_url = 'http://www.chia-anime.me/episode/maou-gakuin-no-futekigousha-shijou-saikyou-no-maou-no-shiso' \
                         '-tensei' \
                         '-shite-shison-tachi-no-gakkou-e/ '

    testSpider = ChiaAnimeSpider(arg_anime_page_url)

    subpage_links = testSpider.chia_xtract_all_episodes_subpage_links()
    # TODO: VAR: start and end for subpage_links to slice the list

    vid_cdn_links = testSpider.xtract_video_links(epi_subpage_links=subpage_links)

    dwn_links = testSpider.xtract_dwnload_links(vid_cdn_links[:2])

    # TODO: use dicts instead of list, helpful to rename the download file.
    print(dwn_links)
    #
    # # TODO: DEBUG Testing Anime Search.
    # search_res = ChiaAnimeSpider.search_chia('Shingeki no Kyojin')

    # print(ChiaAnimeSpider.chia_anime_supermeta_data(arg_anime_page_url))
