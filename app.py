import flask

from data import specs

app = flask.Flask('__name__')


@app.route('/planner')
def planner():
    events = {100: 'BAM', 120: 'BAM2', 11: 'hoj', 105: 'MEGABAM'}
    return flask.render_template('brtn_test.html', seconds=15*60, events=events)


@app.route('/')
def index():
    return flask.render_template('index.html', specs=specs)


if __name__ == '__main__':
    app.run(debug=True)
