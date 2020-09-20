import flask_sqlalchemy  # type: ignore


db = flask_sqlalchemy.SQLAlchemy()


class Record(db.Model):  # type: ignore
    hash = db.Column(db.String(), nullable=False, primary_key=True)
    layout = db.Column(db.JSON(), nullable=False)

    def __repr__(self):
        return '<Record %r>' % self.hash


if __name__ == '__main__':
    db.create_all()
