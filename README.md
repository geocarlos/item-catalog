# Item Catalog

This is the third project for the Udacity Full Stack Web Developer Nanodegree

It is a Flask application designed to hold a list of items (a catalog) separated by category.


## Requirements

- Python (I have used Python 2.7.12 for development and testing)
- Flask
- SQLAlchemy
- oauth2client

oauth2client is implemented for Google and Facebook. That requires credentials configuration on Google and Facebook. For local development, Facebook must be provided with a domain name other than "localhost" (please refer to the ending of the "app.py" file). Facebook also requires https and the IP of your server (your public IP) must be entered in the app advanced settings on Facebook.

If you are using a virtual machine with Vagrant to run the application, the configuration for making 127.0.0.1 show another domain name other than 'localhost' must be in your host machine.

### Files you need to create for oAuth in the root foder

For Google, you need to include the file client_secrets.json with the following information:

`{
  "web": {
    "client_id": "[YOUR_APP_CLIENT_ID].apps.googleusercontent.com",
    "project_id": "catalog-application-206115",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://accounts.google.com/o/oauth2/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "[YOUR_APP_CLIENT_SECRET]",
    "redirect_uris": ["https://localhost:5000/catalog"],
    "javascript_origins": ["https://localhost:5000"]
  }
}`

For Facebook, you need to include the file fb_client_secrets.json with the following information:

`{
  "web": {
    "app_id": "[YOUR_APP_ID]",
    "app_secret": "[YOUR_APP_SECRET]"
  }
}`

### Initial data for tests

The file add_some_items.py is a script to enter initial data for testing. You may want to edit it.

## Run the application

Once you have the required Python modules installed, you may start the application with

`python app.py`

If you leave the app.py file as is, and everything works just fine, you may view the application on https://localhost:5000 or https://catalogapplication.com:5000

In case you want HTTP, instead of HTTPS, you will have to remove "ssl_context='adhoc'" from app.run, at the ending of the app.py file, and your Google oAuth settings will need to include http://localhost:5000.  
