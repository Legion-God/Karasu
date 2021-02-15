from sites.chiaanime import ChiaAnimeSpider
from hurry.filesize import size
import requests
from tqdm import tqdm

# TODO: pass the search result anime page url here
test_anime_page_url = 'http://www.chia-anime.me/episode/maou-gakuin-no-futekigousha-shijou-saikyou-no-maou-no-shiso' \
                      '-tensei' \
                      '-shite-shison-tachi-no-gakkou-e/ '


def downloader(tuple_anime_download):
    """
    Handles the downloading stuff for single video.
    :param tuple_anime_download: tuple: (video_download_link, filename_for_the_video)
    :return:
    """
    episode_link, filename = tuple_anime_download
    episode_response = requests.get(episode_link, stream=True)
    total_size = int(episode_response.headers['content-length'])

    print(f'Starting Download of {filename}')
    print(f'Total Size {size(total_size)}')

    # TODO: REMOVE: hacky way to avoid adding video to vcs.
    filename = '../../' + filename

    filename += '.mp4'
    chunk_size = 1024
    num_bars = int(total_size)

    # Shows the episode number that is downloading
    desc = ChiaAnimeSpider.find_epi_num_in_title(filename)
    desc = 'Episode ' + desc + ' '
    # Tqdm is updating manually, coz originally it won't show correct units.
    with open(filename, 'wb') as f, tqdm(total=num_bars,
                                         unit='B', unit_scale=1, unit_divisor=1024, leave=True, desc=desc) as pbar:
        for chunk in episode_response.iter_content(chunk_size=chunk_size):
            if chunk:
                dwn_size = f.write(chunk)
                pbar.update(dwn_size)

    print(f'Download Done {filename}')


def batch_download(start_episode, end_episode, anime_url):
    """
    Slices the episodic subpage links and downloads the videos in batch
    :param start_episode: int: start episode from 1 (inclusive)
    :param end_episode: int: ending episode (inclusive)
    :param anime_url: str: anime subpage url link.
    :return:
    """
    # TODO: think about extracting functions as params, pass the params to the function to make usable for other sites.
    anime_obj = ChiaAnimeSpider(anime_url)
    anime_epi_subpage_links = anime_obj.chia_xtract_all_episodes_subpage_links()

    sliced_subpage_links = anime_epi_subpage_links[start_episode - 1:end_episode]
    anime_cdn_links = anime_obj.xtract_video_cdn_links(epi_subpage_urls=sliced_subpage_links)

    for link in anime_cdn_links:
        tuple_anime = anime_obj.xtract_direct_dwn_link_selenium(link)
        downloader(tuple_anime_download=tuple_anime)

    return anime_cdn_links


def single_download(episode, anime_url):
    """
    Wrapper around the batch downloader for downloading single episode.
    :param episode: int: episode number.
    :param anime_url: str: anime subpage url link
    :return:
    """
    batch_download(start_episode=episode, end_episode=episode, anime_url=anime_url)


# TODO: testing delete this in prod
if __name__ == '__main__':
    print(batch_download(start_episode=1, end_episode=1, anime_url=test_anime_page_url))
