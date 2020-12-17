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


"""
class Ability(db.Model):  # type: ignore
    spell_id = db.Column(db.String(), nullable=False)
    name = db.Column(db.String(), nullable=False, primary_key=True)
    duration = db.Column(db.String(), nullable=False)
    cool_down = db.Column(db.String(), nullable=False)
    _spec = db.Column(db.String(), db.ForeignKey('Specialization.name'), nullable=False)
    is_default = db.Column(db.Boolean(), nullable=False)


class Specialization(db.Model):  # type: ignore
    name = db.Column(db.String(), nullable=False, primary_key=True)
    color_main = db.Column(db.String(), nullable=False)
    color_cd = db.Column(db.String(), nullable=False)
    abilities = db.relationship('Ability', backref='spec', lazy=True)
"""


if __name__ == '__main__':
    db.create_all()
