"""Search view tests."""

from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, connect_db, User, Clinic, Vet, Review, Favorite

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database
os.environ['DATABASE_URL'] = "postgresql:///baffv-test"

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False

class SearchViewTestCase(TestCase):
    """Test views for vet search."""

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
            self.uid1 = user1.id

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

            rv2 = Review(user_id=self.uid1,
                         vet_id=self.vid2,
                         rating=3,
                         comment="OK.")
            db.session.add(rv2)
            db.session.commit()
            self.rid2 = rv2.id

            f1 = Favorite(user_id=self.uid1, vet_id=self.vid1)
            f2 = Favorite(user_id=self.uid1, vet_id=self.vid2)
            db.session.add_all([f1, f2])
            db.session.commit()
            
    def tearDown(self):
        """Clean up after each test."""
        with app.app_context():
            db.drop_all()
            db.session.remove()

    def test_home_page_search_no_login(self):
        """Can I search for vets without logging in?"""

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['search_area'] = '12345'

            # Search by zip code
            # resp = c.post('/')
            # self.assertEqual(resp.status_code, 302)

            resp = c.post('/results', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Test Vet1', html)
            self.assertIn('Test Vet2', html)
            self.assertNotIn('Test Vet3', html)

            # Search by city & state
            with c.session_transaction() as sess:
                sess['search_area'] = 'Test City, TS'

            resp = c.post('/results', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Test Vet1', html)
            self.assertIn('Test Vet2', html)
            self.assertNotIn('Test Vet3', html)

            # Search only by city
            with c.session_transaction() as sess:
                sess['search_area'] = 'Test City'

            resp = c.post('/results', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Test Vet1', html)
            self.assertIn('Test Vet2', html)
            self.assertNotIn('Test Vet3', html)

    def test_home_page_search_login(self):
        """Can I search for vets after logging in?"""

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.uid1
                sess['search_area'] = '12345'

            resp = c.post('/results', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Test Vet1', html)
            self.assertIn('Test Vet2', html)
            self.assertNotIn('Test Vet3', html)
