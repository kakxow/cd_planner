from concurrent.futures import ThreadPoolExecutor
from functools import partial
from itertools import chain
from types import SimpleNamespace
from typing import List, Tuple, TypedDict

import requests

import convert
from settings import wcl_key


MYTHIC_DIFFICULTY = 5
ONLY_KILLS = 2
API = 'https://www.warcraftlogs.com/v1/{}'
KEY = {'api_key': wcl_key}
EXCLUDE = [
    'Melee',
    'Stagger'
]


class Event(TypedDict):
    name: str
    color: str
    casts: List[str]


Fight = SimpleNamespace
Abilities = List[SimpleNamespace]
Events = List[Event]


class Layout(TypedDict):
    seconds: int
    name: str
    phases: list
    boss_actions: Events


def get_zones() -> List[SimpleNamespace]:
    url_zones = API.format('zones')
    response = requests.get(url_zones, KEY)
    return convert.json_to_list_sns(response.text, 'str')


def get_rankings(id: str, difficulty: str) -> List[SimpleNamespace]:
    """difficulty 1 = LFR, 2 = Flex, 3 = Normal, 4 = Heroic, 5 = Mythic"""
    url_rankings = API.format(f'rankings/encounter/{id}')
    params = {
        **KEY,
        'metric': 'progress',
        'difficulty': difficulty,
        'partition': 1,
    }
    with ThreadPoolExecutor() as p:
        get_page = partial(_get_page, params, url_rankings)
        logs = list(chain.from_iterable(p.map(get_page, range(1, 10))))

    return logs[:100]


def _get_page(params: dict, url_rankings: str, page: int) -> List[SimpleNamespace]:
    p = {**params}
    p.update({'page': page})  # type: ignore
    response = requests.get(url_rankings, p)
    if response.status_code != 200:
        return []
    data = convert.json_to_sns(response.text, 'str')
    logs = [log for log in data.rankings if log.reportID and not log.exploit]
    return logs


def get_fight(log_id: str, fight_id: str) -> Fight:
    url_fights = API.format(f'report/fights/{log_id}')
    params = {
        **KEY,  # type: ignore
        'translate': True
    }
    response = requests.get(url_fights, params)
    data = convert.json_to_sns(response.text, 'str')
    fight = [f for f in data.fights if str(f.id) == fight_id][0]
    return fight


def get_damage_taken(log_id: str, fight_id: str) -> Tuple[Fight, Abilities]:
    abilities: Abilities = []
    fight = get_fight(log_id, fight_id)
    url_tables = API.format(f'report/tables/damage-taken/{log_id}')
    params = {
        **KEY,
        'start': fight.start_time,
        'end': fight.end_time,
        'by': 'ability',
        'translate': True,
    }
    response = requests.get(url_tables, params)  # type: ignore
    data = convert.json_to_sns(response.text, 'str')
    for abl in data.entries:
        if abl.name in EXCLUDE or not abl.hitdetails:
            continue
        ability = SimpleNamespace(
            name=abl.name,
            guid=abl.guid,
            damage=abl.total,
            hit=abl.hitdetails[0].max
        )
        abilities.append(ability)
    return fight, abilities


def get_events(log_id: str, fight_id: str) -> Tuple[Fight, Events]:
    events = []
    fight, abilities = get_damage_taken(log_id, fight_id)
    abilities.sort(key=lambda x: x.damage, reverse=True)
    url_events = API.format(f'report/events/damage-taken/{log_id}')
    params = {
            **KEY,
            'start': fight.start_time,
            'end': fight.end_time,
            'translate': True,
        }
    with ThreadPoolExecutor() as p:
        get_event = partial(_get_event, params, fight.start_time, url_events)
        events = list(p.map(get_event, abilities[:10]))
    return fight, events


def _get_event(
    params: dict,
    start_time: int,
    url_events: str,
    abl: SimpleNamespace
) -> Event:
    p = {**params, 'abilityid': abl.guid}
    # p.update({'abilityid': abl.guid})
    response = requests.get(url_events, p)  # type: ignore
    data = convert.json_to_sns(response.text, 'str')
    casts_ms = {event.timestamp-start_time for event in data.events}
    casts = list({convert.ms_to_str(cast) for cast in casts_ms})
    casts.sort()
    event = Event(
            name=abl.name,
            color='rgb(245, 140, 186)',
            casts=casts
    )
    return event


def get_layout(log_id: str, fight_id: str) -> Layout:
    fight, boss_actions = get_events(log_id, fight_id)
    fight_duration = fight.end_time - fight.start_time
    layout = Layout(
        seconds=fight_duration // 1000,
        name=fight.name,
        phases=[],
        boss_actions=boss_actions
    )
    # with open(f'{log_id}.json', 'w') as f:
    #     json.dump(layout, f)
    return layout


"""
Get zones -> zone_id's, enc_id's, partitions
Select a boss -> enc_id
Get rankings for a given enc_id.
    metric=progress, difficulty=5, partition=last, page
From rankings -> duration, report_id, fight_id
Get report/fights/report_id. find fight_id's start and end
Get report/tables/damage-taken/report_id.
    start=,end=, hostility=0 (default),by=ability
from data -> name, guid, abilityIcon, hitdetails.total
Get report/events/damage-taken/report_id. abilityid=guid
data =>  timestamp; tick=False!!!

Admin flow:
    List all fights -> Select one.
    List top100 open logs (by progress) -> Select a log
    Save to DB as BossRecord(boss_name, guild_name, layout)

"""
