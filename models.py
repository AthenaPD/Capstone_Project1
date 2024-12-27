"""Models for Fear Free Vets."""
from datetime import datetime
from statistics import mean

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """Connect this database to Flask app."""
    db.app = app
    db.init_app(app)


class Clinic(db.Model):
    """Table for veterinarian clinics."""

    __tablename__ = "clinics"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    street_address = db.Column(db.String)
    city = db.Column(db.String, nullable=False)
    state = db.Column(db.String, nullable=False)
    zip_code = db.Column(db.String)
    phone = db.Column(db.String)
    website = db.Column(db.String)

    vets = db.relationship('Vet', backref='clinic')

    def __repr__(self):
        """Representation of the clinic object."""
        return f"<Clinic #{self.id}: {self.name}>"

    @property
    def location(self):
        location = f"{self.street_address}, {self.city}, {self.state} {self.zip_code}"
        return location.strip("None, ")


class Vet(db.Model):
    """Table for veterinarians."""

    __tablename__ = "vets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.id', ondelete='CASCADE'))

    # id on ff website, used to ensure I don't add the same vet more than once
    fear_free_id = db.Column(db.Integer, nullable=False, unique=True)

    reviews = db.relationship('Review', back_populates='vet')

    def __repr__(self):
        """Representation of the vet object."""
        return f"<Vet #{self.id}: {self.name}>"
    
    @property
    def average_rating(self):
        """Get the average rating of this vet."""

        ratings = [r.rating for r in self.reviews]
        return round(mean(ratings), 1) if len(ratings) > 0 else 0


class User(db.Model):
    """Table for users."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    favorites = db.relationship('Vet', secondary="favorites")

    reviews = db.relationship('Review', back_populates='user')

    def __repr__(self):
        """Readable representation of a user instance."""
        return f'<User #{self.id}: {self.username}, {self.email}>'

    @property
    def full_name(self):
        """Returen full name of user."""
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def signup(cls, first_name, last_name, username, email, password):
        """Sign up user.

        Hashes password and adds user to database.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(first_name=first_name, last_name=last_name, username=username, email=email, 
                    password=hashed_pwd)
        
        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password and,
        if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """
        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        
        return False


class Favorite(db.Model):
    """Table for users' favorite vets."""

    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    vet_id = db.Column(db.Integer, db.ForeignKey('vets.id', ondelete='cascade'))

    def __repr__(self):
        """Representation of the favorite object."""
        return f"<Favorite #{self.id}: User#{self.user_id} Vet#{self.vet_id}>"

    def serialize(self):
        """Returns a dict representation of the favorite object created."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "vet_id": self.vet_id
        }


class Review(db.Model):
    """Table for users' reviews."""

    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    vet_id = db.Column(db.Integer, db.ForeignKey('vets.id', ondelete='cascade'))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())
    rating = db.Column(db.Numeric(precision=2, scale=1), nullable=False)
    comment = db.Column(db.Text)

    user = db.relationship('User', back_populates='reviews')
    vet = db.relationship('Vet', back_populates='reviews')

    def __repr__(self):
        """Representation of the review object."""
        return f"<Review #{self.id}: User#{self.user_id} Vet#{self.vet_id}>"
    
    def serialize(self):
        """Returns a dict representation of the review object."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'vet_id': self.vet_id,
            'timestamp': self.timestamp,
            'rating': self.rating,
            'comment': self.comment
        }
