"""Clinic model tests."""

# To run these tests in terminal:
# python -m unittest test_user_model.py

from app import app
import os
from unittest import TestCase

from models import db, Clinic, Vet

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///baffv-test"

# Now we can import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data


class ClinicModelTestCase(TestCase):
    """Test clinic model."""

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
        
    def tearDown(self):
        """Clean up after each test."""
        with app.app_context():
            db.drop_all()
            db.session.remove()

    def test_clinic_model(self):
        """Does basic model work?"""

        with app.app_context():

            clns = Clinic.query.all()
            self.assertEqual(len(clns), 1)

            cln = Clinic.query.get(self.cid)

            # test location property
            self.assertEqual(cln.location, '123 Test Ave., Test City, TS 12345')

    def test_link_vets(self):
        """Does the link with a vet works?"""
        with app.app_context():

            vt = Vet(name='Test Vet',
                     clinic_id=self.cid,
                     fear_free_id=12345)
            
            db.session.add(vt)
            db.session.commit()

            cln = Clinic.query.get(self.cid)
            self.assertEqual(len(cln.vets), 1)
            self.assertEqual(cln.vets[0].name, 'Test Vet')
            