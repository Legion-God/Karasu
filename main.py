from selenium import webdriver
import requests
from bs4 import BeautifulSoup
from hurry.filesize import size

'''
anime_site_url = 'http://www.chia-anime.me/'
'''

# VAR: anime_page_url
arg_anime_page_url = 'http://www.chia-anime.me/episode/maou-gakuin-no-futekigousha-shijou-saikyou-no-maou-no-shiso-tensei' \
                     '-shite-shison-tachi-no-gakkou-e/ '


class AnimeSpider:
    """
    Class for extracting and downloading anime episodes.
    """

    def __init__(self, anime_page_url):
        """
        Prepares the object for crawling.
        :param anime_page_url: pass the anime page url of chia anime.
        """
        self.anime_page_url = anime_page_url

    def xtract_all_episodes_subpage_links(self):
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
        sub_page_links = []

        for div_soup in div_sliced_post_soup:
            link_soup = div_soup.find('a')
            sub_page_links.insert(0, link_soup['href'])

        # Delete this in production.
        for episode, link in enumerate(sub_page_links, 1):
            print(f'Episode:{episode} and link:{link}')

        return sub_page_links

    def xtract_video_links(self, web_driver, epi_subpage_links):
        """
        Extracts downloaded video links from the list slice of subpage links.
        :param web_driver: webDriver.
        :param epi_subpage_links: slice of list of episode page links.
        :return: returns a list of downloadable video links.
        """
        download_links = []
        # Testing the first link.
        # Use request and bs4 to get cdn links
        # then click on the html element and extract data using selenium.
        # //body/div[1]/div[1]/div[1]/div[2]/video[1]
        # this is the xpath
        pass

    # Class end


testSpider = AnimeSpider(arg_anime_page_url)

subpage_links = testSpider.xtract_all_episodes_subpage_links()

# Initialize the webDriver
driver = webdriver.Edge('msedgedriver.exe')
