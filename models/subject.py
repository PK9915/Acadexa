from database.database import db


class Subject(db.Model):

    __tablename__ = "subjects"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    code = db.Column(
        db.String(30),
        nullable=True
    )

    teacher = db.Column(
        db.String(100),
        nullable=True
    )

    semester = db.Column(
        db.Integer,
        nullable=True
    )

    description = db.Column(
        db.String(255),
        nullable=True
    )

    user_id = db.Column(
        db.Integer,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def __repr__(self):

        return f"<Subject {self.name}>"