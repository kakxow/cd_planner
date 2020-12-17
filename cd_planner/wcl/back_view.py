import datetime as dt
import json

import flask

from . import back
from .layout_utils import filter_layout
from cd_planner.db import db, BossRecord
from cd_planner.utils.helpers import create_hash

views = flask.Blueprint('back_views', __name__, url_prefix='/back')


@views.route('/')
def back_index():
    """
    Returns zone list.
    """
    zones = back.get_zones()
    return flask.render_template('back_index.html', zones=zones)


@views.route('/<fight_id>')
def ranks(fight_id: str):
    """
    Returns list of logs for given fight_id - unique encounter identifier.
    """
    rankings = back.get_rankings(fight_id, '5')
    return flask.render_template('back_index.html', rankings=rankings)


@views.route('/log/<log_id>', methods=['GET', 'POST'])
def log(log_id: str):
    """
    Renders a planner layout for given log and fight IDs.
    """
    fight_id = flask.request.args.get('fightID', default='', type=str)
    _layout: back.Layout

    if flask.request.method == 'GET':
        # Show ability breakdown.
        _layout = back.build_layout(log_id, fight_id)
        boss_name = _layout['name']
        layout_name = flask.request.args.get('name', default='', type=str)
        flask.session['_layout'] = _layout
        return flask.render_template(
            'back_index.html',
            record_name=layout_name,
            events=_layout['boss_actions'],
            boss_name=boss_name
        )

    _layout = flask.session.pop('_layout', back.build_layout(log_id, fight_id))
    boss_name = _layout['name']
    form = flask.request.form.to_dict()
    layout_name = form.pop('name')
    include = form.values()
    _layout = filter_layout(_layout, include)
    layout = json.dumps(_layout)
    boss_record = BossRecord(
        boss_name=boss_name,
        layout=layout,
        record_name=layout_name,
        added=dt.datetime.now(),
        hash=create_hash(layout)
    )
    db.session.merge(boss_record)
    try:
        db.session.commit()
    except Exception as e:
        print(e, e.args)
    return flask.redirect(flask.url_for(
        'views.load_boss',
        boss_name=boss_name,
        record_name=layout_name
    ))
