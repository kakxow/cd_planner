import flask

from data import specs, START_POS, TOTAL_TIME

app = flask.Flask(__name__, static_url_path='')


@app.route('/planner')
def planner():
    events = {100: 'BAM', 120: 'BAM2', 11: 'hoj', 105: 'MEGABAM'}
    return flask.render_template(
        'brtn_test.html',
        seconds=TOTAL_TIME,
        events=events,
        specs=specs,
        start_pos=START_POS
    )


@app.route('/')
def index():
    return flask.render_template('index.html', specs=specs)


@app.route('/data.py')
def serve_data():
    return flask.send_file('data.py')


if __name__ == '__main__':
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(debug=True)
