from flask import Flask, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
#from flask_bootstrap import Bootstrap5
import datetime
import os
import requests
from dotenv import load_dotenv
import logging


# setup server logging and format 
logging.basicConfig(filename='logging.log', level=logging.DEBUG, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

# Removed logging.DEBUG from basicConfig so it wouldnt display API key
#level=logging.DEBUG

SECRET_KEY = os.urandom(32)

# make a class to inherint from the FlaskForm Class 
class SearchForm(FlaskForm):
    #from fields type and labels
    location = StringField(label="location", validators=[DataRequired()], render_kw={"placeholder":"37.802297,-122.405844"})
    submit = SubmitField(label="Search")


#get the year for the footer
current_year = datetime.datetime.now().year

# get environment variables
load_dotenv()
BING_MAP_KEY = os.getenv('BING_MAP_KEY')



# create the flask app
app = Flask(__name__)

# secret key for wtfform csrf 
app.config['SECRET_KEY'] = SECRET_KEY




@app.route('/', methods=["POST", "GET"])
def home():    
    # makes an object of the login class
    search_form = SearchForm()

    # validate on submit will be true if the validaiton was sucessfull
    if search_form.is_submitted():
        

        # get the submitted location
        location = search_form.location.data

        logging.info(location)

        #get the locaiton time zone
        params = {"key": BING_MAP_KEY
                  }

        url = f"https://dev.virtualearth.net/REST/v1/TimeZone/{location}"


        try:
            response = requests.get(url, params=params)
            response.raise_for_status()

            #logging.info(response)

            json_data = response.json()
            local_time = json_data["resourceSets"][0]["resources"][0]["timeZone"]["convertedTime"]["localTime"]

            #print(json_data)
            #print(local_time)



        except requests.HTTPError as error:
            print("Failed to retrieve timezone data. HTTP Error:", error)
        except Exception as error:
            print("An error occurred with the timezone:", error) 


        #set the Bing maps API request paramaters
        params = {"dir":"90", 
                  "ms":"700,500",
                  "key": BING_MAP_KEY
                  }

        url = f"https://dev.virtualearth.net/REST/V1/Imagery/Map/Birdseye/{location}/22"
        
        # params = {
        #     "mapSize":"500,400",
        #     "key": BING_MAP_KEY
        # }

        # url = f"https://dev.virtualearth.net/REST/v1/Imagery/Map/AerialWithLabels/{location}"


        try:
            #make the request to the API
            response = requests.get(url, params=params)
            response.raise_for_status()


            #get the response body containing the image
            image_data = response.content

            # Save the image locally
            with open('static/assets/img/image.jpg', 'wb') as f:
                f.write(image_data)

            img_location = "../static/assets/img/image.jpg"

        except requests.HTTPError as error:
            print("Failed to retrieve timezone data. HTTP Error:", error)
        except Exception as error:
            print("An error occurred with the timezone:", error)

        
        return render_template('result.html', year=current_year,img_location=img_location, local_time=local_time, location=location)


    return render_template('index.html', year=current_year, form=search_form)


@app.route('/result', methods=["POST"])
def result():

    return render_template('result.html', year=current_year)



if __name__ == "__main__":
    app.run(debug=True)





