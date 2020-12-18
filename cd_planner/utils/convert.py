from collections import defaultdict
import datetime as dt
import json
from types import SimpleNamespace
from typing import Dict, List, Union

from cd_planner.db import BossRecord
from . import data


def bosses_to_dict(bosses: List[BossRecord]) -> Dict[str, List[str]]:
    d: Dict[str, List[str]] = defaultdict(list)
    for boss in bosses:
        d[boss.boss_name].append(boss.record_name)
    return d


def json_to_sns(s: str, mode: str) -> SimpleNamespace:
    """ Modes - 'file' for filename or 'str'. """
    if mode == 'file':
        file_name = s
        with open(file_name) as f:
            d = json.load(f, object_hook=lambda x: SimpleNamespace(**x))
    elif mode == 'str':
        d = json.loads(s, object_hook=lambda x: SimpleNamespace(**x))
    else:
        raise ValueError('Mode should be "file" or "str"')
    return d


def json_to_list_sns(s: str, mode: str) -> List[SimpleNamespace]:
    """ Modes - 'file' for filename or 'str'. """
    if mode == 'file':
        file_name = s
        with open(file_name) as f:
            d = json.load(f, object_hook=lambda x: SimpleNamespace(**x))
    elif mode == 'str':
        d = json.loads(s, object_hook=lambda x: SimpleNamespace(**x))
    else:
        raise ValueError('Mode should be "file" or "str"')
    return d


def enhance_data(d: SimpleNamespace) -> SimpleNamespace:
    new_obj = d
    # for phase in new_obj.encounter.phases:
    #     phase.intervals = [interval_to_px(interval)
    #                        for interval in phase.intervals]

    for action in new_obj.encounter.boss_actions:
        action.casts = [time_to_sec(cast) for cast in action.casts]

    for specialization in new_obj.layout:
        spec_name = specialization.spec.name
        spec_obj = data.specs_dict[spec_name]
        specialization.spec = spec_obj
        for player in specialization.players:

            for ability in player.abilities:
                ability_obj = data.abilities_dict[ability.name]
                for arg, val in vars(ability_obj).items():
                    setattr(ability, arg, val)
                ability.casts_px = [time_to_px(cast) for cast in ability.casts]
    return new_obj


def change(ability) -> None:
    ability_obj = data.abilities_dict[ability.name]
    for arg, val in vars(ability_obj).items():
        setattr(ability, arg, val)


def interval_to_px(interval: List[str]) -> List[int]:
    # ["0:30", "0:55"] -> [296, 421]
    start, end = interval
    return [time_to_px(start), time_to_px(end)]


def time_to_px(s: str) -> int:
    # Converts seconds to pixels "0:30" -> 296
    # Takes data.SCALE in account and adds 1 pixel (pre scale) for border.
    sec = time_to_sec(s)
    if not sec:
        return 0
    return (sec + 1) * data.SCALE


def px_to_time(px: Union[int, str, float]) -> str:
    # Converts pixels to seconds 296 -> "0:30" or "296px" -> "0:30"
    if isinstance(px, str):
        px = float(px[:-2])
    time_stamp = int((px - data.START_POS) / data.SCALE)
    return f'{time_stamp // 60}:{time_stamp % 60:02d}'


def time_to_sec(s: str) -> int:
    # Convert time to seconds "0:30" -> 30
    time = dt.datetime.strptime(s, '%M:%S')
    return time.second + time.minute * 60 + time.hour * 60 * 60


def ms_to_str(ms: int) -> str:
    sec = int(ms / 1000)
    return f'{sec//60}:{sec%60:02d}'


def phases(p) -> dict:
    res = {}
    for name, periods in p.items():
        periods = [(time_to_px(period[0]), time_to_px(period[1]))
                   for period in periods]
        res[name] = periods
    return res


def invert_boss_casts(bc) -> dict:
    inverted: Dict[int, str] = defaultdict(str)
    for name, periods in bc.items():
        seconds = (time_to_sec(ts) for ts in periods)
        for sec in seconds:
            if inverted[sec]:
                inverted[sec] = ', '.join([inverted[sec], name])
            else:
                inverted[sec] = name
    return inverted


def boss_casts(bc) -> dict:
    res = {}
    for name, periods in bc.items():
        res[name] = [time_to_px(ts) for ts in periods]
    return res


if __name__ == '__main__':
    with open('new.json') as f:
        d = json.load(f)
    with open('pretty.json', 'w') as f:
        json.dump(d, f, indent=4)
