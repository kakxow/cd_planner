import flask_sqlalchemy  # type: ignore


db = flask_sqlalchemy.SQLAlchemy()


class Record(db.Model):  # type: ignore
    hash = db.Column(db.String(), nullable=False, primary_key=True)
    added = db.Column(db.DateTime(), nullable=False)
    layout = db.Column(db.JSON(), nullable=False)

    def __repr__(self):
        return '<Record %r>' % self.hash


class BossRecord(db.Model):  # type: ignore
    hash = db.Column(db.String(), nullable=False)
    boss_name = db.Column(db.String(), nullable=False, primary_key=True)
    record_name = db.Column(db.String(), nullable=False, primary_key=True)
    added = db.Column(db.DateTime(), nullable=False)
    layout = db.Column(db.JSON(), nullable=False)


if __name__ == '__main__':
    db.create_all()
