import requests
import json

"""
    Handles radio streaming for Kpop, Jpop and anime themes.
"""


def search_theme(anime_name):
    """
    Returns the results dict with direct links to anime themes
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


"""
A dict of radio stream urls
"""


def redirect_url(original_url):
    """
    Returns the redirected url radio stream
    :param original_url: str: original url
    :return: str: redirected radio stream
    """
    return requests.get(original_url, stream=True).url


# noinspection SpellCheckingInspection
radio_urls = {'jpop_listen_moe': 'https://listen.moe/stream',
              'everything_weeb': 'https://s3.radio.co/sff133d65b/listen',
              'jpop_alter': 'https://streamingv2.shoutcast.com/japanimradio',
              'anime': redirect_url('https://stream.laut.fm/animefm'),
              'kpop_listen_moe': 'https://listen.moe/kpop/stream',
              'eurobeat': redirect_url('https://stream.laut.fm/eurobeat'),
              'vocaloid': 'http://curiosity.shoutca.st:8019/stream',
              'synthwave': 'http://air.radiorecord.ru:805/synth_320',
              'synthwave_alter': 'https://stream.nightride.fm/nightride.m4a',
              'dance': 'https://www.ophanim.net:8444/s/9780',
              'dance_alter': redirect_url('https://stream.laut.fm/dance'),
              'dubstep': 'https://stream.24dubstep.pl/radio/8000/mp3_best',
              'dubstep_247': 'https://radio.maddubz.net/radio/8000/dubstep.mp3',
              'dubstep_alter': 'https://ice6.somafm.com/dubstep-128-mp3',
              'country': 'https://pureplay.cdnstream1.com/6029_128.mp3',
              'amazing_80s': redirect_url('https://stream.amazingradios.com/80s'),
              'heavy_metal': redirect_url('https://stream.laut.fm/metal'),
              'lo_fi': redirect_url('https://laut.fm/lofi'),
              'chill': redirect_url('https://stream.laut.fm/loungetunes'),
              'hip_hop': redirect_url('https://stream.laut.fm/1000hiphop')
              }

'''
everthing_weeb contains, classic, modern anime, city pop, eurobeat and video game music.
'''


if __name__ == '__main__':
    # TODO: for testing
    results_dict = search_theme('Dororo')
    print(json.dumps(results_dict, indent=4))
