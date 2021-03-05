import requests
from bs4 import BeautifulSoup
from collections import namedtuple

'''
Extracts and translates the anime schedule list
'''


def xtractor_list():
    """
    Xtracts the anime list schedule and returns the namedtuple
    :return: Weekday(['day', Show(['show_name', 'episode', 'time'])])
    """
    schedule_list_url = 'https://animeschedule.net/'
    list_resp = requests.get(schedule_list_url)
    raw_soup = BeautifulSoup(list_resp.text, 'html.parser')
    days_soup = raw_soup.find_all('div', id='timetable')[0]
    days_soup = days_soup.find_all('div', class_='timetable-column')
    Show = namedtuple('Show', ['show_name', 'episode', 'time'])
    Weekday = namedtuple('Weekday', ['day', 'shows'])
    show_list = []
    for show_item in days_soup:
        day = show_item.find('h1', class_='timetable-column-day').get_text()
        div_soup = show_item.find_all('div', class_=['timetable-column-show', 'compact'])

        # Temporary storing the shows for each weekdays and then adding them to single day namedtuple
        temp_show_list = []
        for day_show in div_soup:
            episode = day_show.find('span', class_='show-episode').get_text(strip=True)

            # Stripping new lines and stuff from episode number.
            episode = (lambda ep: ' '.join(ep.split()))(episode)
            air_time = day_show.find('span', class_='show-air-time').get_text(strip=True)
            show_title = day_show.find('h2', class_='show-title-bar').get_text(strip=True)
            temp_show_list.append(Show(show_name=show_title, episode=episode, time=air_time))

        show_list.append(Weekday(day=day, shows=temp_show_list))

    # # TODO: TESTING, prints list schedule.
    # for i in show_list:
    #     print(f'Day: {i.day}')
    #     print('-------------------')
    #     for j in i.shows:
    #         print(f'{j}')
    #     print('-------------------')
    return show_list


if __name__ == '__main__':
    xtractor_list()
