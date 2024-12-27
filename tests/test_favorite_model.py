"""Favorite model tests."""

# To run these tests in terminal:
# python -m unittest test_user_model.py

from app import app
import os
from unittest import TestCase

from models import db, User, Vet, Favorite, Clinic

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///baffv-test"

# Now we can import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data


class FavoriteModelTestCase(TestCase):
    """Test favorite model."""

    def setUp(self):
        """Add sample data."""
        with app.app_context():
            db.create_all()

            u = User.signup(
                first_name='test',
                last_name='user1',
                email="test1@test.com",
                username="testuser1",
                password="HASHED_PASSWORD1"
            )
            db.session.commit()
            self.uid = u.id

            cln = Clinic(name='test_clinic',
                         street_address='123 Test Ave.',
                         city='Test City',
                         state='TS',
                         zip_code='12345')
            db.session.add(cln)
            db.session.commit()
            self.cid = cln.id

            vt = Vet(name='Test Vet',
                     clinic_id=self.cid,
                     fear_free_id=12345)
            db.session.add(vt)
            db.session.commit()
            self.vid = vt.id
        
    def tearDown(self):
        """Clean up after each test."""
        with app.app_context():
            db.drop_all()
            db.session.remove()

    def test_favorite_model(self):
        """Test the basic stuffs."""
        with app.app_context():
            f1 = Favorite(user_id=self.uid, vet_id=self.vid)
            db.session.add(f1)
            db.session.commit()

            # Test the repr function
            self.assertEqual(f'{Favorite.query.get(f1.id)}', f'<Favorite #{f1.id}: User#{self.uid} Vet#{self.vid}>')
            # Test the serialize function
            self.assertEqual(f1.serialize(), {'id': f1.id, 'user_id': self.uid, 'vet_id': self.vid})

    def test_add_favorite(self):
        """Add a vet to favorite."""

        with app.app_context():

            # User started with 0 favorite vet.
            user = User.query.get(self.uid)
            self.assertEqual(len(user.favorites), 0)

            # Add a favorite vet
            f1 = Favorite(user_id=self.uid, vet_id=self.vid)
            db.session.add(f1)
            db.session.commit()

            # Now there should be 1 favorite vet.
            user = User.query.get(self.uid)
            self.assertEqual(len(user.favorites), 1)

            # Remove favorite vet
            db.session.delete(f1)
            db.session.commit()

            # Now there should be no favorite vet again.
            self.assertEqual(len(user.favorites), 0)
            