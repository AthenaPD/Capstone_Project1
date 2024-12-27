"""Review model tests."""

# To run these tests in terminal:
# python -m unittest test_user_model.py

from app import app
import os
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


class ReviewModelTestCase(TestCase):
    """Test review model."""

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

            rv = Review(user_id=self.uid,
                        vet_id=self.vid,
                        rating=3,
                        comment="Don't like nor dislike.")
            db.session.add(rv)
            db.session.commit()
            self.rid = rv.id
        
    def tearDown(self):
        """Clean up after each test."""
        with app.app_context():
            db.drop_all()
            db.session.remove()

    def test_review_model(self):
        """Does basic model work?"""
        with app.app_context():
            u = User.query.get(self.uid)
            v = Vet.query.get(self.vid)
            r = Review.query.get(self.rid)

            self.assertEqual(len(u.reviews), 1)
            self.assertEqual(len(v.reviews), 1)
            self.assertEqual(v.reviews[0].user_id, self.uid)
            self.assertEqual(u.reviews[0].vet_id, self.vid)
            self.assertEqual(r.user.username, 'testuser1')
            self.assertEqual(r.vet.name, 'Test Vet')
            self.assertEqual(f'{Review.query.get(self.rid)}', f'<Review #{self.rid}: User#{self.uid} Vet#{self.vid}>')
            r_serialized = r.serialize()
            self.assertEqual(r_serialized['comment'], "Don't like nor dislike.")
            self.assertEqual(r_serialized['id'], self.rid)
            self.assertIsInstance(r_serialized, dict)
