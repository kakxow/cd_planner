import flask

from . import db
from .wcl import back_view
from .planner import views


def create_app(conf: str):
    # conf in Prod, Dev, Test
    app = flask.Flask(__name__, static_url_path='')
    app.config.from_object(f'config.{conf}')

    db.db.init_app(app)

    app.register_blueprint(views.views)
    app.register_blueprint(back_view.views)
    return app


if __name__ == '__main__':
    app = create_app('Dev')
    app.run(debug=True)
