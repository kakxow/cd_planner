import copy
import hashlib
from types import SimpleNamespace
from typing import List

import flask

from . import convert
from cd_planner.db import BossRecord, db
from .const import DEFAULT_LAYOUT


def boss_from_name(
    bosses: List[SimpleNamespace],
    boss_name: str
) -> SimpleNamespace:
    boss = filter(lambda el: el.name == boss_name, bosses)
    return copy.deepcopy(next(boss))


def create_hash(d: str) -> str:
    hash_object = hashlib.sha1(bytes(d, 'utf-8'))
    hash_ = hash_object.hexdigest()
    return hash_[-7:]


def default_data() -> SimpleNamespace:
    d = convert.json_to_sns('default.json', 'file')
    return convert.enhance_data(d)


def data_from_hash(hsh: str) -> SimpleNamespace:
    raw_data = db.Record.query.filter_by(hash=hsh).first()
    if not raw_data:
        flask.abort(404)
    d = convert.json_to_sns(raw_data.layout, 'str')
    return d


def default_layout(boss: BossRecord) -> SimpleNamespace:
    d = copy.deepcopy(DEFAULT_LAYOUT)
    d.encounter = convert.json_to_sns(boss.layout, 'str')
    return d
