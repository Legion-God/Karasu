from selenium import webdriver
import requests
from bs4 import BeautifulSoup
from hurry.filesize import size
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep, perf_counter
import re

'''
Supported Anime Sites.
chia_anime_url = 'http://www.chia-anime.me/'
'''


def find_epi_num_in_title(page_title):
    """
    Helper function to extract the episode number from the page title using regex and returns epi_number
    :param page_title: page title of the anime video player
    :return: string with epi_number
    """
    epi_number_regex = re.compile('Episode ([0-9]+)')
    return epi_number_regex.findall(page_title)[0]


# TODO: REMOVE perf_counter in production.


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
        # Initialize the webDriver
        # TODO: make it headless
        self.driver = webdriver.Edge('msedgedriver.exe')

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
        direct_dwnload_links = []

        for episode in epi_cdn_links:
            direct_dwnload_links.append(xtract_player_selenium(episode, self.driver))

        # Close the browser after extracting all the direct dwn links.
        self.driver.quit()
        return direct_dwnload_links


def xtract_player_selenium(player_cdn_link, anim_webdriver):
    """
    returns a direct download video from a given cdn link
    :param player_cdn_link: single cdn link.
    :param anim_webdriver: expects a webDriver for selenium
    :return: single direct download link.
    """
    # Extract this element 'src' after clicking on the video player
    # //body/div[1]/div[1]/div[1]/div[2]/video[1]
    # TODO: keep clearing cookies when making request to cdn link to fetch direct download link.
    anim_webdriver.get(player_cdn_link)
    print(f'Scraping {anim_webdriver.title}')

    # Play the player
    anim_webdriver.find_element_by_xpath('//body/div[1]/div[1]/div[1]/div[9]/div[1]/div[1]/div[1]/div['
                                         '2]/div[1]').click()

    try:
        sleep(5)
        # Switch to ad iframe
        wait(anim_webdriver, 10).until(
            EC.frame_to_be_available_and_switch_to_it(anim_webdriver.find_element_by_xpath('//body/div[1]/div[1]/div['
                                                                                           '1]/div[2]/iframe[1]')))

        print("DEBUG: Switched to ad iframe ...")
        # Find the ad skip button
        # TODO: IMP: Use webdriver wait and EC to find and locate the element
        wait(anim_webdriver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '/html[1]/body[1]/div[1]/div[1]/a[1]'))).click()

        # anim_webdriver.find_element_by_xpath('/html[1]/body[1]/div[1]/div[1]/a[1]').click()
        print('DEBUG: Ad Skipped!')

    except Exception as e:
        # TODO: In production if failed to retrieve a episode link then just return "Try again" message and proceed
        #  with collected links.
        print(e)
        print("Failed to Skip Ad, possible errors: Can't find the target element or Timeout Exception")
        # TODO: refactor ad skipper and handle for situation when ads are not skipped.
        # anim_webdriver.close()
    else:
        # Switch back to content
        anim_webdriver.switch_to.default_content()
        print('DEBUG: Switched to default content ...')
        anim_webdriver.delete_all_cookies()
        print('All cookies deleted ...')

    vid_dwn_element = anim_webdriver.find_element_by_xpath('//body/div[1]/div[1]/div[1]/div[2]/video[1]')
    vid_dwn_link = vid_dwn_element.get_attribute('src')

    print(f'Done {anim_webdriver.title}')
    return vid_dwn_link


# TODO: VAR: anime_page_url
arg_anime_page_url = 'http://www.chia-anime.me/episode/maou-gakuin-no-futekigousha-shijou-saikyou-no-maou-no-shiso' \
                     '-tensei' \
                     '-shite-shison-tachi-no-gakkou-e/ '

testSpider = ChiaAnimeSpider(arg_anime_page_url)

all_epi_tic = perf_counter()
subpage_links = testSpider.xtract_all_episodes_subpage_links()
# TODO: VAR: start and end for subpage_links to slice the list
all_epi_toc = perf_counter()

print(f'Xtract all episodes Benchmark: {all_epi_toc - all_epi_tic:0.3f}')
vid_cdn_links = testSpider.xtract_video_links(epi_subpage_links=subpage_links)

dwn_epi_tic = perf_counter()
dwn_links = testSpider.xtract_dwnload_links(vid_cdn_links)
dwn_epi_toc = perf_counter()

print(f'Xtract direct download links Benchmark: {dwn_epi_toc - dwn_epi_tic:0.3f}')
# TODO: use dicts instead of list, helpful to rename the download file.
print(dwn_links)
