import os
import re

from flask import Flask, render_template, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm, ReviewForm, VetSearchForm
from models import db, connect_db, User, Review, Favorite, Vet, Clinic

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///bay_area_fear_free_vets'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

##########################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get_or_404(session[CURR_USER_KEY])
    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.
    
    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(first_name=form.first_name.data, last_name=form.last_name.data,
                               username=form.username.data, email=form.email.data, 
                               password=form.password.data)
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)
        
        do_login(user)
        return redirect('/')

    return render_template('users/signup.html', form=form)
    
@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(username=form.username.data, password=form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.first_name}!", "success")
            return redirect("/")
        
        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)

@app.route('/logout')
def logout():
    """Handel logout of user."""

    do_logout()
    flash('You are logged out!', 'info')
    return redirect('/')


##########################################################################
# Pages for general audience without login
@app.route('/', methods=['GET', 'POST'])
def search_page():
    """Home page with a search bar for fear-free vets."""
    form = VetSearchForm()

    if form.validate_on_submit():
        session['search_area'] = form.zipcode_or_city.data.strip()
        return redirect('/results')

    return render_template('home.html', form=form)

#Search results page 
@app.route('/results', methods=['GET', 'POST'])
def found_vets():
    """Page to show found vets and allow additional searches via js."""

    form = VetSearchForm()

    if form.validate_on_submit():
        session['search_area'] = form.zipcode_or_city.data.strip()
        return redirect('/results')
    
    search_area = session.get('search_area', None)

    zipcode = re.search(r"\b\d{5}\b", search_area)
    city_name = re.search(r"\s*(\w+\s*\w*)\s*", search_area)

    if zipcode:
        # user typed in a zip code.
        zipcode = zipcode.group()
        vets = Vet.query.join(Clinic, Clinic.id==Vet.clinic_id).filter(Clinic.zip_code==zipcode).all()
    elif city_name:
        # user typed in a city name.
        city = city_name.group(1).lower().title()
        vets = Vet.query.join(Clinic, Clinic.id==Vet.clinic_id).filter(Clinic.city==city).all()
    else:
        # error handling if user didn't type in the correct search format
        flash("Incorrect input format. Please type in either the zip code or name of your city. i.e. 95510 or San Jose", "danger")
        return redirect('/')

    if not vets:
        flash("Did NOT find any matches. Please try typing in another zip code or city name.", "info")
        return redirect('/')
    
    return render_template('vets/found_vets.html', vets=vets, form=form)


##########################################################################
# User route:
@app.route('/users/<int:user_id>')
def user_profile(user_id):
    """Show user profile."""

    if not g.user:
        flash("Access unauthorized. Please sign up or log in!", "danger")
        return redirect("/")
    
    # User can only see his/her own profile.
    if g.user.id != user_id:
        flash("You are not authorized to see this page!", "danger")
        return redirect('/')
    
    reviews = Review.query.filter(Review.user_id==user_id).order_by(Review.timestamp.desc()).limit(5).all()

    return render_template('users/user_profile.html', vets=g.user.favorites, reviews=reviews)

# Edit User route??

##########################################################################
# Clinic route:
@app.route('/clinics/<int:clinic_id>')
def clinic_profile(clinic_id):
    """Show info about a clinics and the vets who work there."""

    clinic = Clinic.query.get_or_404(clinic_id)

    return render_template('clinics/clinic_profile.html', clinic=clinic, vets=clinic.vets)

##########################################################################
# Vet route:
@app.route('/vets/<int:vet_id>')
def vet_profile(vet_id):
    """Show detailed info about a vet."""

    vet = Vet.query.get_or_404(vet_id)

    return render_template('vets/vet_profile.html', vet=vet, reviews=vet.reviews)

##########################################################################
# Review route:
@app.route('/reviews/<int:vet_id>/add', methods=['GET', 'POST'])
def add_review(vet_id):
    """Add a review:
    Show form if GET. If valid,  add review and redirect to user page.
    """

    if not g.user:
        flash("Please sign up or log in first!", "danger")
        return redirect('/login')

    form = ReviewForm()
    vet = Vet.query.get_or_404(vet_id)

    if form.validate_on_submit():
        review = Review(user_id=g.user.id, vet_id=vet_id, rating=form.rating.data, comment=form.comment.data)
        g.user.reviews.append(review)
        db.session.commit()

        return redirect(f'/vets/{vet_id}')
    
    return render_template('reviews/add_review.html', form=form, vet=vet)

@app.route('/reviews')
def all_reviews():
    """Get all reviews of current user and display them on a page."""

    if not g.user:
        flash("Please sign up or log in first!", "danger")
        return redirect('/login')
    
    reviews = Review.query.filter(Review.user_id==g.user.id).order_by(Review.timestamp.desc()).all()

    return render_template('reviews/all_reviews.html', reviews=reviews)

##########################################################################
# Custom Error Handling Pages
@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 not found page."""
    return render_template('errors/custom_404_not_found_page.html'), 404

@app.errorhandler(401)
def unauthorized(e):
    """Custom 401 page when users are not authenticated or not authorized."""
    return render_template('errors/custom_401_unauthorized_page.html'), 401

#####################################################################################
# API Routes
#####################################################################################
# Favorite routes:

@app.route('/api/users/favorite/<int:vet_id>', methods=['POST'])
def change_favorite(vet_id):
    """
    Add/remove a favorite vet for the currently-logged-in user.
    A JS script on the client side will call this route to change the favorite status of a vet.
    """

    if not g.user:
        flash("Please login to add a vet to your favorite!", "danger")
        return redirect('/login')
    
    vet = Vet.query.get_or_404(vet_id)

    favorite = Favorite.query.filter(Favorite.user_id==g.user.id, Favorite.vet_id==vet_id).one_or_none()

    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify(message=f"{vet.name} removed from favorite!")
    else:
        new_fave = Favorite(user_id=g.user.id, vet_id=vet_id)
        db.session.add(new_fave)
        db.session.commit()
        serialized = new_fave.serialize()
        return (jsonify(favorite=serialized), 201)
    
# Get the ids of all favorite vets if the user is logged in.
@app.route('/api/users/favorites')
def get_favorites():
    """Get the ids of all favorite vets if the user is logged in."""

    if not g.user:
        flash("Access denied. Please login first!", "danger")
        return redirect('/login')
    
    favorites = [vet.id for vet in g.user.favorites]
    serialized = {'ids': favorites}

    return jsonify(favorite_vets=serialized)

#####################################################################################
# Review routes:
@app.route('/api/reviews/<int:review_id>')
def get_review(review_id):
    """Return JSON of the data in the requested review."""

    review = Review.query.get_or_404(review_id)
    serialized = review.serialize()

    return jsonify(review=serialized)
