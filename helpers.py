import base64
import copy
from types import SimpleNamespace
from typing import List

import flask

import convert
from db import db
from const import BOSSES, DEFAULT_LAYOUT


def boss_from_name(
    bosses: List[SimpleNamespace],
    boss_name: str
) -> SimpleNamespace:
    boss = filter(lambda el: el.name == boss_name, bosses)
    return copy.deepcopy(next(boss))


def create_hash(d: str) -> str:
    raw_hash = str(abs(hash(d)))
    bytes_hash = bytes([int(x) for x in raw_hash])
    return base64.b64encode(bytes_hash).decode()


def default_data() -> SimpleNamespace:
    d = convert.json_to_sns('default.json', 'file')
    return convert.enhance_data(d)


def data_from_hash(hsh: str):
    raw_data = db.Record.query.filter_by(hash=hsh).first()
    if not raw_data:
        flask.abort(404)
    d = convert.json_to_sns(raw_data.layout, 'str')
    return d


def default_layout(boss_name: str):
    d = copy.deepcopy(DEFAULT_LAYOUT)
    d.encounter = boss_from_name(BOSSES, boss_name)
    return d
