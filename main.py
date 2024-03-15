from flask import Flask, render_template, url_for, redirect, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError, PasswordField
from wtforms.validators import DataRequired, Email, Length
#from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime, os, requests
from dotenv import load_dotenv
import logging

# this project utilizes previous projects code as well as some starter code from 100 Days of python


# setup server logging and format 
logging.basicConfig(filename='logging.log', level=logging.DEBUG, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

# Removed logging.DEBUG from basicConfig so it wouldnt display API key
#level=logging.DEBUG


# custom from validator for lat long
def lat_long_validate(form, field):
    lat_long= field.data
    if lat_long != "":
        try:
            lat, long = map(float, lat_long.split(','))
            if not (-90 <= lat <= 90) or not (-180 <= long <= 180):
                raise ValidationError('Invalid coordinates format. Enter a valid latitude and longitude.')
        except ValueError:
            raise ValidationError('Invalid coordinates format. Enter latitude and longitude separated by a comma only.')


#get the year for the footer
current_year = datetime.datetime.now().year

# get environment variables
load_dotenv()
BING_MAP_KEY = os.getenv('BING_MAP_KEY')
SECRET_KEY = os.urandom(32)


# create the flask app
app = Flask(__name__)

#get the year for the footer
current_year = datetime.datetime.now().year


# secret key for wtfform csrf 
app.config['SECRET_KEY'] = SECRET_KEY

# CREATE DATABASE
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# create a flask login manager
login_manager = LoginManager()
login_manager.init_app(app)

# user_loader callback to reload user object from the user id stored in the session
# returns non if the ID is not valid
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# CREATE TABLE IN DB and implement it as a flask login user class as well with UserMixin
# To make implementing a user class easier, you can inherit from UserMixin, which provides default implementations for all of these properties and methods. (It’s not required, though.)
# Note: A Mixin is simply a way to provide multiple inheritance to Python. This is how you add a Mixin:
class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))


with app.app_context():
    db.create_all()


# make a class to inherint from the FlaskForm Class 
class SearchForm(FlaskForm):
    #from fields type and labels
    location = StringField(label="location", validators=[DataRequired(),lat_long_validate],  render_kw={"placeholder":"37.802297,-122.405844"})
    location_two = StringField(label="location", validators=[lat_long_validate],  render_kw={"placeholder":"optional"})
    submit = SubmitField(label="Search")

# Create a register form
class RegisterForm(FlaskForm):
    # form fields types and labels
    name = StringField(label='Name', validators=[DataRequired()])
    email = StringField(label='Email', validators=[DataRequired(), Email(message='That\'s not a valid email address.')])
    password = PasswordField(label='Password', validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters.")])

# Create a login form
class LoginForm(FlaskForm):
    # form fields types and labels
    email = StringField(label='Email', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])


@app.route('/', methods=["POST", "GET"])
def home():
   # GET response
    return render_template('index.html', year=current_year, logged_in=current_user.is_authenticated) 



@app.route('/search', methods=["POST", "GET"])
def search():    
    # makes an object of the login class
    search_form = SearchForm()

    # validate on submit will be true if the validation was successful
    if search_form.validate_on_submit():
        # get the submitted location
        location = search_form.location.data
        location_two = search_form.location_two.data
        logging.info(location)











        #get the location time zone--------------------
        params = {"key": BING_MAP_KEY
                  }
        url = f"https://dev.virtualearth.net/REST/v1/TimeZone/{location}"
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            #logging.info(response)
            json_data = response.json()
            local_time = json_data["resourceSets"][0]["resources"][0]["timeZone"]["convertedTime"]["localTime"]
            local_time = local_time.replace("T", " ")
            #print(json_data)
            print(local_time)


        except requests.HTTPError as error:
            print(f"{error_details}. Timezone request HTTP Error:", error)
            return render_template('index.html', year=current_year, form=search_form)
        # Handle timeout error
        except requests.exceptions.Timeout:        
            print("The request timed out, please try again later or check internet connection")
        except Exception as error:
            print("An error occurred with the timezone:", error)
            local_time = f"Local time for this location is not available due to {error}"
  


        #set the Bing maps API request paramaters for a static map---------------
        if location_two == "":
            # Paramaters for an image     
            params = {
                    "key": BING_MAP_KEY,                 
                    "zoomLevel" : "20", 
                    "ms":"700,500",                   
                    }
            
            #  AerialWithLabels, Aerial,  AerialWithLabelsOnDemand,  BirdsEye,  BirdsEyeWithLabels,  Road,  CanvasDark, 
            imagerySet = "BirdsEyeWithLabels"
            centerPoint = location       
            
            # Static map url
            url = f"https://dev.virtualearth.net/REST/V1/Imagery/Map/{imagerySet}/{centerPoint}"

        else:
            # paramaters for a route between two points
            params = {
                    "key": BING_MAP_KEY,               
                    }
            imagerySet = "AerialWithLabelsOnDemand"
            # Get a map that displays a route without specifying a center point. You can choose to specify the map area or you can accept the default
            url = f"https://dev.virtualearth.net/REST/v1/Imagery/Map/{imagerySet}/Routes?wp.0={location};64;1&wp.1={location_two};66;2"


        img_location = "../static/assets/img/image.jpg"
        error_details = ""
        try:
            #make the request to the API
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            #get the response body containing the image
            
            image_data = response.content
            #json_data = response.json()
            #error_details = json_data["errorDetails"]

            # Save the image locally
            with open('static/assets/img/image.jpg', 'wb') as f:
                f.write(image_data)

            

        except requests.HTTPError as error:
            print(f"{error_details}. Image request HTTP Error:", error)
            # Handle timeout error
        except requests.exceptions.Timeout:        
            print("The request timed out, please try again later or check internet connection")
        except Exception as error:
            print("An error occurred with the image:", error)


        # get weather from partner microservice -------------------
        lat_long_list = location.split(",")
        weather_api = "https://unit-convertering.vercel.app/api/weather"
        error_details = ""
        local_weather = ""

        params = {
            "latitude": lat_long_list[0],
            "longitude": lat_long_list[1]
        }    

        try:
            response = requests.get(weather_api, params=params, timeout=10) 
            response.raise_for_status()
            json_data = response.json()
            print(json_data)
            local_weather = json_data['body']

        # Handle HTTP errors
        except requests.HTTPError as error:
            print(f"{error_details}. Weather request HTTP Error:", error)
        # Handle timeout error
        except requests.exceptions.Timeout:        
            print("The request timed out, please try again later or check internet connection")
        # Handle other errors
        except Exception as error:
            print("An error occurred with the weather:", error)


        # POST response
        return render_template('result.html', 
                               year=current_year, 
                               img_location=img_location, 
                               local_time=local_time, 
                               location=location,
                               local_weather=local_weather)


    # GET response
    return render_template('search.html', year=current_year, form=search_form, logged_in=current_user.is_authenticated)




@app.route('/register', methods=["POST", "GET"])
def register():
    register_form = RegisterForm()
 # validate on submit will be true if the validaiton was sucessfull
    if register_form.validate_on_submit():
        email = register_form.email.data
        result = db.session.execute(db.select(User).where(User.email == email))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        if user:
            # User already exists
            flash("That email already exists, pick a new one or log in instead!")
            return redirect(url_for('login'))

        # Salt the password for security
        hashed_salted_pass = generate_password_hash(
            register_form.password.data, 
            method='pbkdf2:sha256',             
            salt_length=4)
            
        new_user = User(
                    name = register_form.name.data,
                    email = register_form.email.data,
                    password = hashed_salted_pass
                    )

        # write user class credentials to database
        db.session.add(new_user)
        db.session.commit()

        # login user
        login_user(new_user)
        flash('Logged in successfully.')

        return redirect(url_for('search', user_name=register_form.name.data))
        #return render_template("secrets.html", user_name=register_form.name.data)

    return render_template("register.html", form=register_form, logged_in=current_user.is_authenticated)
    #return render_template('register.html', form=register_form)


@app.route('/login', methods=["POST", "GET"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        #get from info
        email = login_form.email.data
        password = login_form.password.data

       
        # Find user by email entered getting a user object back
        query1 = db.session.execute(db.select(User).where(User.email == email))
        user = query1.scalar()
        if not user:
            flash("Email does not exist, please try again")
            return redirect(url_for('login', form=login_form)) 

        # Check stored password hash against entered password hashed.
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login', form=login_form))            

        else:
            login_user(user)
            return redirect(url_for('search'))       


    return render_template("login.html", form=login_form, logged_in=current_user.is_authenticated)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))



if __name__ == "__main__":
    app.run(debug=True)





