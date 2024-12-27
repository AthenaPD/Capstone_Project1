from app import db, app
from models import Clinic, User, Review, Favorite, Vet
import pandas as pd
from sqlalchemy import insert
import json

df_vets = pd.read_csv("scraped_data/vets.csv")

df_clinics = pd.read_csv("scraped_data/clinics.csv")
df_clinics['zip_code'] = df_clinics['zip_code'].apply(lambda z: f'{z:.0f}' if not pd.isna(z) else z)

clinics = json.loads(df_clinics.to_json(orient='records'))
vets = json.loads(df_vets.to_json(orient="records"))


with app.app_context():

    db.drop_all()
    db.create_all()

    # Add vets and clinics from web-scraped data.
    db.session.execute(insert(Clinic), clinics)
    db.session.execute(insert(Vet), vets)

    # Add one test user
    orion = User(first_name='Orion', last_name='PanDeka', username='OrionPD', email='orionpd@gmail.com', password='$2b$12$hDBiRnR6ZyKXEt8Hg6u5ZeK.eJshorlWC.hFSPo8wRkHNdDvOCKFy')
    aria = User(first_name='Aria', last_name='Chu', username='AChu', email='aria_chu@yahoo.com', password='$2b$12$qjKtNPSw1OtFguoWV1d/7uj358A4ZdaEHkIXC4.Dd8SMMhfYZY4l6')
    athena = User(first_name='Athena', last_name='Pan', username='APan', email='athena_pan@gmail.com', password='$2b$12$06Sjr14ZPiFz.weE4a3bXeLoKS9nBrOYEAmFAHlh/5iyl3ak8BfUy')
    db.session.add_all([orion, aria, athena])
    db.session.commit()

    # Add favorite vets for Orion
    orion_fav1 = Favorite(user_id=1, vet_id=7)
    orion_fav2 = Favorite(user_id=1, vet_id=8)
    orion_fav3 = Favorite(user_id=1, vet_id=9)
    orion_fav4 = Favorite(user_id=1, vet_id=10)
    orion_fav5 = Favorite(user_id=1, vet_id=11)
    orion_fav6 = Favorite(user_id=1, vet_id=12)
    orion_fav7 = Favorite(user_id=1, vet_id=13)
    orion_fav8 = Favorite(user_id=1, vet_id=14)

    db.session.add_all([orion_fav1, orion_fav2, orion_fav3, orion_fav4, 
                        orion_fav5, orion_fav6, orion_fav7, orion_fav8])
    db.session.commit()

    # Add a review
    orion_goh_review = Review(user_id=1, vet_id=7, rating=5, 
                              comment="We really liked Dr. Goh. She was nice, patient and very mindful about building a relationship with us and our pup, Orion! We'd absolutely recommend her to anyone looking for a fear-free vet!")
    orion_review_2 = Review(user_id=1, vet_id=13, rating=3, 
                            comment="Dr. Hermansen is good. However, we didn't like the clinic she works at. They can't guarantee that we can accompany our pet during all appointments, especially for technician-only appointments, which doesn't work for our anxious pup.")
    orion_review_3 = Review(user_id=1, vet_id=9, rating=3, 
                            comment="We like this doc, but we didn't like the clinic she works at. They can't guarantee that we can accompany our pet during all appointments, especially for technician-only appointments, which doesn't work for our anxious pup.")
    orion_review_4 = Review(user_id=1, vet_id=10, rating=3, 
                            comment="We like this doc, but we didn't like the clinic she works at. They can't guarantee that we can accompany our pet during all appointments, especially for technician-only appointments, which doesn't work for our anxious pup.")
    orion_review_5 = Review(user_id=1, vet_id=11, rating=3, 
                            comment="We like this doc, but we didn't like the clinic she works at. They can't guarantee that we can accompany our pet during all appointments, especially for technician-only appointments, which doesn't work for our anxious pup.")
    orion_review_6 = Review(user_id=1, vet_id=14, rating=3, 
                            comment="We like this doc, but we didn't like the clinic she works at. They can't guarantee that we can accompany our pet during all appointments, especially for technician-only appointments, which doesn't work for our anxious pup.")
    aria_review_1 = Review(user_id=2, vet_id=7, rating=5, 
                            comment="My experience with the veterinary team has been exceptional. Despite my dog's reluctance to visit the vet, the staff's professionalism and kindness have made each visit much more manageable. The clinic's team is not only highly skilled but also incredibly understanding. They handle my dog's anxiety with patience and care, ensuring that he feels as comfortable as possible during his appointments. Their approach is always gentle and reassuring, which has helped alleviate my dog's fears over time. What stands out about this veterinary clinic is their dedication to providing a positive experience for both pets and their owners. They take the time to explain procedures thoroughly and answer any questions I have, which has been immensely reassuring. In addition to their expertise, the clinic's facilities are clean and well-maintained, further enhancing the overall experience. I appreciate their attention to detail in every aspect of pet care.")
    aria_review_2 = Review(user_id=2, vet_id=4, rating=3, comment='We think this vet is ok, but not special.')
    athena_review_1 = Review(user_id=3, vet_id=4, rating=2, comment='We did not like this vet. :(')

    db.session.add_all([orion_goh_review, orion_review_2, orion_review_3, orion_review_4, orion_review_5, 
                        orion_review_6, aria_review_1, aria_review_2, athena_review_1])
    db.session.commit()
    