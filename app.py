# Importing necessary modules
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


# Setting up the Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///safespace.db' # Database URI
app.secret_key = 'my-secret-key'
db = SQLAlchemy(app)      # Initializing the SQLAlchemy database instance

# Setting up the login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Defining the user loader callback for the login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Defining routes and associated view functions for the application
@app.route('/')
def index():
    # If the user is authenticated, render the homepage with user information
    if current_user.is_authenticated:
        return render_template('homepage.html', current_user=current_user)
    # If not authenticated, render the index page    
    else:
        return render_template('index.html', current_user=current_user)


@app.route('/homepage')
@login_required
def homepage():
    # Render the homepage with user information
    return render_template('homepage.html', current_user=current_user)    


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Handling POST request for user signup
    if request.method == 'POST':
        # Extracting user input from the form
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        first_name = request.form['full_name']
        last_name = request.form['last_name']
        date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d')

        # Validating input and rendering error messages if necessary
        if not email or not password or not first_name or not last_name or not date_of_birth:
            return render_template('signup.html', error='All fields are required.')

        if password != confirm_password:
            return render_template('signup.html', error='Passwords do not match')

        # Hashing password and creating user instance
        hashed_password = generate_password_hash(password)
        user = User(email=email, password=hashed_password, first_name=first_name, last_name=last_name, date_of_birth=date_of_birth)

        # Adding user to the database
        db.session.add(user)
        db.session.commit()

        # Logging in the user and redirecting to the index page
        login_user(user)
        return redirect(url_for('index'))
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Handling POST request for user login
    if request.method == 'POST':
        # Extracting user input from the form
        email = request.form['email']
        password = request.form['password']

        # Querying user from the database
        user = User.query.filter_by(email=email).first()

        # Authenticating user and logging them in if valid
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('homepage'))  # Redirects to the homepage
        else:
            return render_template('login.html', error='Invalid email or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    # Logging out the user and redirecting to the index page
    logout_user()
    return redirect(url_for('index'))

@app.route('/therapists')
def therapists():
    # Render the therapists page
    return render_template('therapists.html')

@app.route('/therapist2')
def therapist2():
    # Querying all therapists from the database
    therapists_list = Therapist.query.all()
    # Rendering the therapist2 page with the therapists list
    return render_template('therapist2.html', therapists=therapists_list)



@app.before_first_request
def create_tables():
    db.create_all()

    # Insert example therapists
    if not Therapist.query.first():
        example_therapists = [
            Therapist(name="Dr. Farida Odewale", credentials="MD, Psychiatrist", image="images/dr_godfred_owusu.jpg"),
            Therapist(name="Dr. Godfred Owusu", credentials="MD, Psychiatrist", image="images/dr_farida_odewale.jpg"),
            Therapist(name="Dr. Kwame Obeng", credentials="PhD, Psychologist", image="images/fred_ola.jpg"),
            Therapist(name="Dr. Abena Peprah", credentials="PhD, Psychologist", image="images/dr_abena_peprah.jpg"),
            Therapist(name="Fred Richards", credentials="LCSW, Therapist", image="images/dr_kwame_obeng.jpg"),
            Therapist(name="Maame Esiri", credentials="LMFT, Therapist", image="images/maame_esiri.jpg")
        ]

        # Adding the example therapists to the database
        for therapist in example_therapists:
            db.session.add(therapist)
        db.session.commit()

#Importing the User and Therapist models
from models import User, Therapist

#Running the application with debug mode enabled
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)


