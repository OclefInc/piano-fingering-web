from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    hand_size = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<UserUpload {self.filename} - Hand Size: {self.hand_size}>'