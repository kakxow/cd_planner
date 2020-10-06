import datetime as dt
import json

import flask

import back
from db import db, BossRecord
from helpers import create_hash

views = flask.Blueprint('back_views', __name__, url_prefix='/back')


@views.route('/')
def back_index():
    zones = back.get_zones()
    return flask.render_template('back_index.html', zones=zones)


@views.route('/<id>')
def ranks(id: str):
    rankings = back.get_rankings(id, '5')
    return flask.render_template('back_index.html', rankings=rankings)


@views.route('/log/<log_id>')
def log(log_id: str):
    fight_id = flask.request.args.get('fightID', default='', type=str)
    guild_name = flask.request.args.get('name', default='', type=str)

    _layout = back.get_layout(log_id, fight_id)
    boss_name = _layout['name']
    layout = json.dumps(_layout)
    boss_record = BossRecord(
        boss_name=boss_name,
        layout=layout,
        record_name=guild_name,
        added=dt.datetime.now(),
        hash=create_hash(layout)
    )
    db.session.merge(boss_record)
    try:
        db.session.commit()
    except Exception as e:
        print(e, e.args)
    return flask.redirect(flask.url_for('views.load_boss', boss_name=boss_name, record_name=guild_name))
