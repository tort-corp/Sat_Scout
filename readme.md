<h1> Sat Scout </h1>

Sat Scout is a Flask based website that will search for satellite imagery of a location using the Bing Maps API. An image will be returned along with some local information. Two points can be searched for as well, in which a route between the two points will be overlaid on a satellite image. A user can create an account and log in if they want their previous searches saved and displayed on the search page. A SQL database is used to store user credentials in a secure manner. 

This project was made following Agile methodologies. The project was broken down into several sprint goals with reflection after each sprint.  

The project is implemented in Python using the Flask framework. Jinja was used for tempting the pages. Bootstrap was used for the front end styling. Several libraries were also used to implement different features. 

WTForms: Form handling as well as form field verification. 
SQAlchemy: ORM between python and the SQL database.
Flask Login: Handled the user object as well as access to different pages and information based on authorization for a user. 
Werkzeug: For password hashing and salting. 
Logging: Logs all requests and errors made.

<h2>Home page</h2>
![home](https://github.com/tort-corp/CS361_sat_scout/assets/46113637/440bb0e7-9af6-4936-80cd-84f7a8f3438a)

<h2>Search Page</h2>
![search](https://github.com/tort-corp/CS361_sat_scout/assets/46113637/c96c0c28-9265-4c06-828f-38f164fea573)

<h2>Results page</h2>
![results](https://github.com/tort-corp/CS361_sat_scout/assets/46113637/d37fe4d9-847c-4402-af7d-0632a439acda)

