"""User view tests."""

from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, User, Clinic, Vet, Favorite, Review

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database
os.environ['DATABASE_URL'] = "postgresql:///baffv-test"

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for user."""

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
            
            db.session.commit()
            self.uid = user1.id

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
                        comment="Do NOT like nor dislike.")
            db.session.add(rv)
            db.session.commit()
            self.rid = rv.id

            fvrt = Favorite(user_id=self.uid, vet_id=self.vid)
            db.session.add(fvrt)
            db.session.commit()
            
    def tearDown(self):
        """Clean up after each test."""
        with app.app_context():
            db.drop_all()
            db.session.remove()

    def test_user_profile(self):
        """When you are logged in, is the user profile page displaying info correctly?"""

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid

            resp = c.get(f'/users/{self.uid}')
            html = resp.get_data(as_text=True)
            self.assertIn('testuser1', html)
            self.assertIn("Do NOT like", html)
            self.assertIn("Test Vet", html)

    def test_add_review(self):
        """Can I add a review?"""

        with app.test_client() as c:
            with app.app_context():
                rvs = Review.query.all()
                self.assertEqual(len(rvs), 1)
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid

            resp = c.post(f'/reviews/{self.vid}/add', data={'rating': 5, 'comment': 'I like this vet more now.'})

            self.assertEqual(resp.status_code, 302)

            with app.app_context():
                rvs = Review.query.all()
                self.assertEqual(len(rvs), 2)
                self.assertEqual(rvs[1].comment, 'I like this vet more now.')
                self.assertEqual(rvs[1].rating, 5)

                vt = Vet.query.get(self.vid)
                self.assertEqual(vt.average_rating, 4)

    def test_all_reviews(self):
        """Can I see all my reviews?"""

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid

            resp = c.get('/reviews')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)

            with app.app_context():
                rvs = Review.query.all()
                self.assertIn('Test Vet', html)
                self.assertIn('Do NOT like nor dislike', html)
