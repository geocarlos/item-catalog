# Item Catalog

This is the third project for the Udacity Full Stack Web Developer Nanodegree

It is a Flask application designed to hold a list of items (a catalog) separated by category.


## Requirements

- Python (I have used Python 2.7.12 for development and testing)
- Flask
- SQLAlchemy
- oauth2client

oauth2client is implemented for Google and Facebook. That requires credentials configuration on Google and Facebook. For local development, Facebook must be provided with a domain name other than "localhost" (please refer to the ending of the "app.py" file). Facebook also requires https and the IP of your server (your public IP) must be entered in the app basic settings on Facebook.

If you are using a virtual machine with Vagrant to run the application, the configuration for making 127.0.0.1 show another domain name other than 'localhost' must be in your host machine.

The file add_some_items.py is a script to enter initial data for testing. You may want to edit. 

## Run the application

Once you have the required Python modules installed, you may start the application with

`python app.py`

If you leave the app.py file as is, and everything works just fine, you may view the application on https://localhost or https://catalogapplication.com

In case you want HTTP, instead of HTTPS, you will have to remove "ssl_context='adhoc'" from app.run, at the ending of the app.py file, and your Google oAuth settings will need to include http://localhost.  
