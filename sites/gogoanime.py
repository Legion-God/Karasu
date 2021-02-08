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

    @staticmethod
    def search_gogo(anime):
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


if __name__ == '__main__':
    GogoAnimeSpider.search_gogo('Naruto')
