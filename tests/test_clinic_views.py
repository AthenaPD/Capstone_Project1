"""Clinic view tests."""

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

class ClinicViewTestCase(TestCase):
    """Test views for clinic."""

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
            
            vt1 = Vet(name='Test Vet1',
                     clinic_id=self.cid,
                     fear_free_id=12345)
            db.session.add(vt1)
            db.session.commit()
            self.vid1 = vt1.id

            vt2 = Vet(name='Test Vet2',
                     clinic_id=self.cid,
                     fear_free_id=67890)
            db.session.add(vt2)
            db.session.commit()
            self.vid2 = vt2.id

            rv1 = Review(user_id=self.uid1,
                         vet_id=self.vid1,
                         rating=3,
                         comment="Do NOT like nor dislike.")
            db.session.add(rv1)
            db.session.commit()
            self.rid1 = rv1.id

            rv2 = Review(user_id=self.uid2,
                         vet_id=self.vid1,
                         rating=5,
                         comment="Great vet!")
            db.session.add(rv2)
            db.session.commit()
            self.rid2 = rv2.id

            rv3 = Review(user_id=self.uid1,
                         vet_id=self.vid2,
                         rating=3,
                         comment="OK.")
            db.session.add(rv3)
            db.session.commit()
            self.rid3 = rv3.id

            rv4 = Review(user_id=self.uid2,
                         vet_id=self.vid2,
                         rating=4,
                         comment="Not bad!")
            db.session.add(rv4)
            db.session.commit()
            self.rid4 = rv4.id
            
    def tearDown(self):
        """Clean up after each test."""
        with app.app_context():
            db.drop_all()
            db.session.remove()

    def test_clinic_profile(self):
        """Is the clinic profile page displaying info correctly?"""

        with app.test_client() as c:
            resp = c.get(f'/clinics/{self.cid}')
            html = resp.get_data(as_text=True)
            self.assertIn('123 Test Ave., Test City, TS 12345', html)
            self.assertIn("Test Vet1", html)
            self.assertIn("Test Vet2", html)
            self.assertIn("3.5", html)
            self.assertIn("4", html)
