"""Vet model tests."""

# To run these tests in terminal:
# python -m unittest test_user_model.py

from app import app
import os
from decimal import Decimal
from unittest import TestCase

from models import db, Clinic, Vet, User, Review

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///baffv-test"

# Now we can import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data


class VetModelTestCase(TestCase):
    """Test vet model."""

    def setUp(self):
        """Add sample data."""
        with app.app_context():
            db.create_all()

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

    def test_vet_model(self):
        """Does basic model work?"""

        with app.app_context():

            vet = Vet.query.get(self.vid)

            # test location property
            self.assertEqual(vet.average_rating, 0)
            self.assertEqual(f'{Vet.query.get(self.vid)}', f'<Vet #{self.vid}: {vet.name}>')

    def test_review_vet(self):
        """Does review changes average rating properly?"""
        with app.app_context():

            u1 = User.signup('Test', 'User1', 'TestUser1', 'testuser1@test.com', 'password1')
            u2 = User.signup('Test', 'User2', 'TestUser2', 'testuser2@test.com', 'password2')
            db.session.commit()

            r1 = Review(user_id=u1.id, vet_id=self.vid, rating=1, comment="Bad Vet!")
            r2 = Review(user_id=u2.id, vet_id=self.vid, rating=5, comment="Great Vet!")
            db.session.add_all([r1, r2])
            db.session.commit()

            vt = Vet.query.get(self.vid)
            self.assertEqual(vt.average_rating, 3.0)

            u3 = User.signup('Test', 'User3', 'TestUser3', 'testuser3@test.com', 'password3')
            db.session.commit()

            r3 = Review(user_id=u3.id, vet_id=self.vid, rating=4, comment="Not bad.")
            db.session.add(r3)
            db.session.commit()

            self.assertEqual(vt.average_rating, Decimal('3.3'))
