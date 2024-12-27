"""User model tests."""

# To run these tests in terminal:
# python -m unittest test_user_model.py

from app import app
import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///baffv-test"

# Now we can import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data


class UserModelTestCase(TestCase):
    """Test user model."""

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            db.create_all()

            u1 = User.signup(
                first_name='test',
                last_name='user1',
                email="test1@test.com",
                username="testuser1",
                password="HASHED_PASSWORD1"
            )

            # Add user to database successfully?
            db.session.commit()

            self.u1_id = u1.id
        
    def tearDown(self):
        """Clean up after each test."""
        with app.app_context():
            db.drop_all()
            db.session.remove()

    def test_user_model(self):
        """Does basic model work?"""

        with app.app_context():

            # There should be two users in total.
            num_user = User.query.all()
            self.assertEqual(len(num_user), 1)

            u1 = User.query.get(self.u1_id)

            # User should have no favorites & no reviews
            self.assertEqual(len(u1.favorites), 0)
            self.assertEqual(len(u1.reviews), 0)

            # Does the repr method work as expected?
            self.assertEqual(f'{User.query.get(self.u1_id)}', f'<User #{self.u1_id}: testuser1, test1@test.com>')
           
            # Does the full_name property work?
            self.assertEqual(u1.full_name, 'test user1')
            
    ####
    #
    # Signup Tests
    #
    ####
    def test_valid_signup(self):
        with app.app_context():
            u_test = User.signup(
                "test", "test", "testtesttest", "testtest@test.com", "password"
            )
            db.session.commit()
            uid = u_test.id
            u_test = User.query.get(uid)
            self.assertEqual(len(User.query.all()), 2)
            self.assertIsNotNone(u_test)
            self.assertEqual(u_test.full_name, "test test")
            self.assertEqual(u_test.username, "testtesttest")
            self.assertEqual(u_test.email, "testtest@test.com")
            self.assertNotEqual(u_test.password, "password")
            # Bcrypt strings should start with $2b$
            self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        with app.app_context():
            User.signup("test", "test", None, "test@test.com", "password")
            with self.assertRaises(exc.IntegrityError) as context:
                db.session.commit()

    def test_invalid_email_signup(self):
        with app.app_context():
            invalid = User.signup("test", "test", "testtest", None, "password")
            with self.assertRaises(exc.IntegrityError) as context:
                db.session.commit()

    def test_invalid_password_signup(self):
        with app.app_context():
            with self.assertRaises(ValueError) as context:
                User.signup("test", "test", "testtest", "email@email.com", "")

            with self.assertRaises(ValueError) as context:
                User.signup("test", "test", "testtest", "email@email.com", None)

    ####
    #
    # Authentication Tests
    #
    ####
    def test_valid_authentication(self):
        with app.app_context():
            u1 = User.query.get(self.u1_id)
            u = User.authenticate(u1.username, "HASHED_PASSWORD1")
            self.assertIsNotNone(u)
            self.assertEqual(u.id, self.u1_id)

    def test_invalid_username(self):
        with app.app_context():
            self.assertFalse(User.authenticate("badusername", "HASHED_PASSWORD1"))

    def test_wrong_password(self):
        with app.app_context():
            u1 = User.query.get(self.u1_id)
            self.assertFalse(User.authenticate(u1.username, "badpassword"))
