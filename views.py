import datetime as dt
import flask

import convert
import data
from db import BossRecord, db, Record
import helpers


views = flask.Blueprint('views', __name__)


@views.route('/favicon.ico')
def favicon():
    return flask.abort(404)


@views.route('/save_layout', methods=['POST'])
def save_layout():
    req = flask.request
    d = req.data.decode()
    h = helpers.create_hash(d)
    db.session.add(Record(hash=h, layout=d, added=dt.datetime.now()))
    try:
        db.session.commit()
    except Exception as e:
        # TODO: may be some obscure shit besides unique constraint.
        print(e, e.args)

    return h


@views.route('/')
@views.route('/planner')
def planner():
    boss = BossRecord.query.first()
    return flask.redirect(f'planner/{boss.boss_name}')


@views.route('/planner/<boss_name>/<record_name>')
def load_boss(boss_name: str, record_name: str):
    print(record_name)
    boss = BossRecord.query.filter_by(
        boss_name=boss_name,
        record_name=record_name
    ).first_or_404()

    bosses = BossRecord.query.all()
    boss_dict = convert.bosses_to_dict(bosses)

    d = helpers.default_layout(boss)
    good_d = convert.enhance_data(d)
    return flask.render_template(
        'render_from_json.html',
        bosses=boss_dict,
        boss=boss.record_name,
        start_pos=data.START_POS,
        scale=data.SCALE,
        data=good_d
    )


@views.route('/planner/<boss_name>')
def default(boss_name: str):
    player_layout = flask.session.pop('player_layout', None)
    if not player_layout:
        boss = BossRecord.query.filter_by(boss_name=boss_name).first_or_404()
        return flask.redirect(f'{boss_name}/{boss.record_name}')

    bosses = BossRecord.query.all()
    boss_dict = convert.bosses_to_dict(bosses)

    d = convert.json_to_sns(player_layout, 'str')
    good_d = convert.enhance_data(d)
    return flask.render_template(
        'render_from_json.html',
        bosses=boss_dict,
        boss=d.encounter.name,
        start_pos=data.START_POS,
        scale=data.SCALE,
        data=good_d
    )


@views.route('/planner/<any_shit>/data.py')
@views.route('/data.py')
def serve_data(any_shit: str = ''):
    return flask.send_file('data.py')


@views.route('/<hsh>')
def load(hsh: str):
    raw_data = Record.query.filter_by(hash=hsh).first()
    if not raw_data:
        flask.abort(404)

    d = convert.json_to_sns(raw_data.layout, 'str')
    flask.session['player_layout'] = raw_data.layout
    return flask.redirect(f'/planner/{d.encounter.name}')


if __name__ == '__main__':
    pass
