"""Vet view tests."""

from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, connect_db, User, Clinic, Vet, Review

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database
os.environ['DATABASE_URL'] = "postgresql:///baffv-test"

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False

class VetViewTestCase(TestCase):
    """Test views for vet."""

    def setUp(self):
        """Add sample data."""
        with app.app_context():
            db.drop_all()
            db.create_all()

            user1 = User.signup(first_name='test',
                                last_name='user1',
                                username="testuser1",
                                email="test1@test.com",
                                password="testuser1")
            
            user2 = User.signup(first_name='test',
                                last_name='user2',
                                username="testuser2",
                                email="test2@test.com",
                                password="testuser2")
            
            db.session.commit()
            self.uid1 = user1.id
            self.uid2 = user2.id

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

            rv1 = Review(user_id=self.uid1,
                         vet_id=self.vid,
                         rating=3,
                         comment="Do NOT like nor dislike.")
            db.session.add(rv1)
            db.session.commit()
            self.rid1 = rv1.id

            rv2 = Review(user_id=self.uid2,
                         vet_id=self.vid,
                         rating=5,
                         comment="Great vet!")
            db.session.add(rv2)
            db.session.commit()
            self.rid2 = rv2.id
            
    def tearDown(self):
        """Clean up after each test."""
        with app.app_context():
            db.drop_all()
            db.session.remove()

    def test_vet_profile(self):
        """Is the vet profile page displaying info correctly?"""

        with app.test_client() as c:
            resp = c.get(f'/vets/{self.vid}')
            html = resp.get_data(as_text=True)
            self.assertIn('Test Vet', html)
            self.assertIn("Write a review", html)
            self.assertIn("test_clinic", html)
            self.assertIn("Great vet!", html)
            self.assertNotIn("testuser3", html)
            self.assertIn("4", html)
