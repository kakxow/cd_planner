import json
from types import SimpleNamespace

import flask

import convert
import data


app = flask.Flask(__name__, static_url_path='')


# @app.route('/planner')
# @app.route('/planner/<boss>')
def planner(boss: str = list(data.bosses)[0]):
    phases, boss_casts = data.bosses[boss]
    return flask.render_template(
        'brtn_test.html',
        bosses=data.bosses,
        seconds=data.TOTAL_TIME,
        events=convert.boss_casts(boss_casts),
        specs=data.specs,
        start_pos=data.START_POS,
        phases=convert.phases(phases),
        selected_boss=boss,
        scale=data.SCALE
    )


@app.route('/')
def index():
    # print(flask.url_for('static', filename='styles/styles.css'))
    return flask.render_template('index.html')


@app.route('/save_layout', methods=['POST'])
def save_layout():
    req = flask.request
    with open('new.json', 'w') as f:
        f.write(req.data.decode())
    return 'OK'


@app.route('/planner')
@app.route('/planner/<boss>')
# @app.route('/from_json')
def from_json():
    with open('default.json') as f:
        d = json.load(f, object_hook=lambda x: SimpleNamespace(**x))
    good_d = convert.fix_data(d)
    return flask.render_template(
        'render_from_json.html',
        bosses=data.bosses,
        seconds=good_d.encounter.seconds,
        start_pos=data.START_POS,
        encounter=good_d.encounter,
        selected_boss=good_d.encounter.name,
        layout=good_d.layout
    )


@app.route('/planner/data.py')
@app.route('/data.py')
def serve_data(any_shit: str = ''):
    return flask.send_file('data.py')


if __name__ == '__main__':
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(debug=True)
