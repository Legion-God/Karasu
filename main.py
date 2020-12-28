from selenium import webdriver
import requests
from bs4 import BeautifulSoup
from hurry.filesize import size
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

'''
anime_site_url = 'http://www.chia-anime.me/'
'''

# VAR: anime_page_url
arg_anime_page_url = 'http://www.chia-anime.me/episode/maou-gakuin-no-futekigousha-shijou-saikyou-no-maou-no-shiso' \
                     '-tensei' \
                     '-shite-shison-tachi-no-gakkou-e/ '


# noinspection SpellCheckingInspection
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

        # TODO: Delete this in production.
        for episode, link in enumerate(sub_page_links, 1):
            print(f'Episode:{episode} and link:{link}')

        return sub_page_links

    def xtract_video_links(self, epi_subpage_links):
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
        pass


def xtract_player_selenium(player_cdn_link, anim_webdriver):
    """
    returns a direct download video from a given cdn link
    :param player_cdn_link: single cdn link.
    :param anim_webdriver: expects a webDriver for selenium
    :return: single direct download link.
    """
    # Extract this element 'src' after clicking on the video player
    # //body/div[1]/div[1]/div[1]/div[2]/video[1]
    anim_webdriver.get(player_cdn_link)

    # Play the player
    anim_webdriver.find_element_by_xpath('//body/div[1]/div[1]/div[1]/div[9]/div[1]/div[1]/div[1]/div['
                                         '2]/div[1]').click()

    try:
        sleep(5)
        # Switch to ad iframe
        wait(anim_webdriver, 10).until(
            EC.frame_to_be_available_and_switch_to_it(anim_webdriver.find_element_by_xpath('//body/div[1]/div[1]/div['
                                                                                           '1]/div[2]/iframe[1]')))

        print("Switched to ad iframe ...")
        # Find the ad skip button
        anim_webdriver.find_element_by_xpath('/html[1]/body[1]/div[1]/div[1]/a[1]').click()
        print('Ad Skipped!')

    except Exception as e:
        print(e)
        print("Failed to Skip Ad, possible errors: Can't find the target element or Timeout Exception")
        anim_webdriver.close()
    else:
        # Switch back to content
        anim_webdriver.switch_to.default_content()
        print('Switched to default content ...')

    vid_dwn_element = anim_webdriver.find_element_by_xpath('//body/div[1]/div[1]/div[1]/div[2]/video[1]')
    vid_dwn_link = vid_dwn_element.get_attribute('src')
    return vid_dwn_link


testSpider = AnimeSpider(arg_anime_page_url)

subpage_links = testSpider.xtract_all_episodes_subpage_links()
vid_cdn_links = testSpider.xtract_video_links(epi_subpage_links=subpage_links)

# Initialize the webDriver
driver = webdriver.Edge('msedgedriver.exe')

# TODO: Test code
xtract_player_selenium(vid_cdn_links[8], driver)

# Approaches to skip the ad and play the video
# Try implicit waits in selenium
# Try to wait for 'src' attribute in target element to appear
# Try polling
# Try to wait for ad to skip automatically and start the video (RISKY)
