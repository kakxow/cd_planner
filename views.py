import flask

import helpers
import data
import db
import convert
from const import BOSSES


views = flask.Blueprint('views', __name__)


@views.route('/save_layout', methods=['POST'])
def save_layout():
    req = flask.request
    d = req.data.decode()
    h = helpers.create_hash(d)
    # with open('new.json', 'w') as f:
    #     f.write(d)
    db.db.session.add(db.Record(hash=h, layout=d))
    try:
        db.db.session.commit()
    except Exception as e:
        # TODO: may be some obscure shit besides unique constraint.
        print(e, e.args)

    return h


@views.route('/planner')
def planner():
    return flask.redirect(f'planner/{BOSSES[0].name}')


@views.route('/planner/<boss_name>')
def default(boss_name: str = BOSSES[0].name):
    if boss_name not in [b.name for b in BOSSES]:
        flask.abort(404)

    raw_data = flask.session.pop('data_from_hash', None)
    if not raw_data:
        d = helpers.default_layout(boss_name)
    else:
        d = convert.json_to_sns(raw_data, 'str')
    good_d = convert.enhance_data(d)
    return flask.render_template(
        'render_from_json.html',
        bosses=[boss.name for boss in BOSSES],
        start_pos=data.START_POS,
        scale=data.SCALE,
        data=good_d
    )


@views.route('/planner/data.py')
@views.route('/data.py')
def serve_data(any_shit: str = ''):
    return flask.send_file('data.py')


@views.route('/<hsh>')
def load(hsh: str):
    raw_data = db.Record.query.filter_by(hash=hsh).first()
    if not raw_data:
        flask.abort(404)

    d = convert.json_to_sns(raw_data.layout, 'str')
    flask.session['data_from_hash'] = raw_data.layout
    return flask.redirect(f'/planner/{d.encounter.name}')


if __name__ == '__main__':
    print(BOSSES)
