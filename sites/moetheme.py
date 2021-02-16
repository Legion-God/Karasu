import requests
import json

"""
    Handles anime theme songs.
"""


def search_theme(anime_name):
    """
    Returns the results dict with direct links to themes
    :param anime_name: str: name of anime
    :return: dict: dict of theme links for streaming and downloading.
    """
    # This url returns the mal id of searched animes, useful for getting theme song data.
    payload_url = f'https://themes.moe/api/anime/search/{anime_name}'

    # It takes list of mal ids as input and returns the direct links to theme songs.
    post_url = 'https://themes.moe/api/themes/search'

    # returns the list of mal ids
    anime_id_payload = requests.get(payload_url).text
    search_results = requests.post(post_url, data=anime_id_payload)

    return json.loads(search_results.text)


if __name__ == '__main__':
    # TODO: for testing
    results_dict = search_theme('Dororo')
    print(json.dumps(results_dict, indent=4))
