from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database_setup import Base, Category, Item, User

from flask import session as login_session, make_response
import random
import string
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db', connect_args={'check_same_thread': False},
                       poolclass=StaticPool)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# AUTHENTICATION STARTS
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state, isLoginPage=True)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    print "Result: %s" % result

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"

    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print "url sent for API access:%s" % url
    print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # Check if user exists, if it doesn't, make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response
# AUTHENTICATION ENDS


@app.route('/')
@app.route('/catalog')
def catalog():
    categories = session.query(Category).all()
    # Items must be sorted by the time they were added
    # so that the "latest items" view will be as expected
    items = sorted(session.query(Item).all(),
                   key=lambda item: item.time_added, reverse=True)
    isLoggedIn = 'username' in login_session  # Switch button Login/Logout
    return render_template('catalog.html', categories=categories, items=items, isLoggedIn=isLoggedIn)

# I don't like when it says that the page was not found just because of
# a slash at the end, but I also don't like the slash to stay there,
# so this is the reason for the redirect below.


@app.route('/catalog/')
def catalogr():
    return redirect(url_for('catalog'))


@app.route('/catalog/<category>/items')
def category(category):
    categories = session.query(Category).all()
    category = filter(lambda cat: cat.name == category, categories)[0]
    items = sorted(session.query(Item).filter_by(
        category_id=category.id).all(), key=lambda item: item.time_added, reverse=True)
    isLoggedIn = 'username' in login_session
    return render_template('catalog.html',
                           categories=categories,
                           items=items,
                           category=category,
                           isLoggedIn=isLoggedIn)


@app.route('/catalog/<category>/<item>')
def item(category, item):
    item = session.query(Item).filter_by(name=item).one()
    # isLoggedIn is used to decide whether to show 'edit' and 'delete' options
    isLoggedIn = 'username' in login_session
    isOwner = 'user_id' in login_session and item.user_id == login_session['user_id']
    return render_template('item.html', item=item, isLoggedIn=isLoggedIn, isOwner=isOwner)


@app.route('/catalog/add', methods=['GET', 'POST'])
def add_item():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = Item(
            name=request.form['name'],
            description=request.form['description'],
            category_id=request.form['category'],
            user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('Successfully added %s'%newItem.name)
        return redirect(url_for('catalog'))
    else:
        categories = session.query(Category).all()
        return render_template('add_item.html', categories=categories,
                               isLoggedIn=True)


@app.route('/catalog/<item>/edit', methods=['GET', 'POST'])
def edit_item(item):
    if request.method == 'POST':
        # Because they the name may have been edited, the id is checked here
        itemToEdit = session.query(Item).filter_by(id=request.form['id']).one()
        itemToEdit.name = request.form['name']
        itemToEdit.description = request.form['description']
        itemToEdit.category_id = request.form['category']
        category = session.query(Category).filter_by(id=itemToEdit.category_id).one()
        session.add(itemToEdit)
        session.commit()
        if(itemToEdit.name == item):
            flash('Item %s successfully updated'%item)
        else:
            flash('Item %s successfully updated to %s'%(item, itemToEdit.name))
        return redirect(url_for('item', category=category.name, item=itemToEdit.name))
    else:
        itemToEdit = session.query(Item).filter_by(name=item).one()
        if 'username' not in login_session:
            return redirect('/login')
        # If user type the URL to edit somebody else's item, they are
        # redirected to the item page
        if itemToEdit.user_id != login_session['user_id']:
            cat = session.query(Category).filter_by(
                id=itemToEdit.category_id).one().name
            flash('You cannot edit this item: not your item')
            return redirect(url_for('item', category=cat, item=item))
        categories = session.query(Category).all()
        return render_template('edit_item.html', categories=categories,
                               item=itemToEdit, isLoggedIn=True)


@app.route('/catalog/<item>/delete', methods=['GET', 'POST'])
def delete_item(item):
    if request.method == 'POST':
        itemToDelete = session.query(Item).filter_by(
            id=request.form['id']).one()
        session.delete(itemToDelete)
        session.commit()
        flash('Item %s successfully deleted'%item)
        return redirect(url_for('catalog'))
    else:
        itemToDelete = session.query(Item).filter_by(name=item).one()
        if 'username' not in login_session:
            return redirect('/login')
        # If user type the URL to delete somebody else's item, they are
        # redirected to the item page
        if itemToDelete.user_id != login_session['user_id']:
            cat = session.query(Category).filter_by(
                id=itemToDelete.category_id).one().name
            flash('You cannot delete this item: not your item')
            return redirect(url_for('item', category=cat, item=item))
        return render_template('delete_item.html', item=itemToDelete, isLoggedIn=True)


# Disconnect based on provider
@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash('You have been logged out.')
    return redirect(url_for('catalog'))


### JSON API ###
"""
Return the whole catalog
"""


@app.route('/catalog.json')
def catalogJSON():
    categories = session.query(Category).all()
    items = session.query(Item).all()
    Categories = [c.serialize for c in categories]
    Items = [i.serialize for i in items]
    for cat in Categories:
        cat['items'] = []
        for item in Items:
            if cat['id'] == item['category_id']:
                cat['items'].append(item)

    return jsonify(Categories=Categories)


"""
Return just a given category with its items
"""


@app.route('/catalog/<category>.json')
def categoryJSON(category):
    try:
        category = session.query(Category).filter_by(name=category).one()
        items = session.query(Item).filter_by(category_id=category.id)
        Categ = category.serialize
        Items = [i.serialize for i in items]
        Categ['items'] = Items
        return jsonify(Category=Categ)
    except:
        return jsonify({'result': 'No %s category was found.' % category})


"""
Return the item that matches the provided id
"""


@app.route('/catalog/json/<item_id>')
def itemJSON(item_id):
    try:
        item = session.query(Item).filter_by(id=item_id).one()
        return jsonify(Item=item.serialize)
    except:
        return jsonify({'result': 'No item with the ID informed.'})

### JSON API ENDS ###


"""
The "ssl_context='adhoc'" configuration is the way I have found to make
Facebook's OAuth work, as it requires 'https'. I also had to add a domain
name to 127.0.0.1, different from 'localhost', which is 'catalogapplication.com',
because facebook did not accept 'localhost' as an authorized domain.
For some reason that I cannot understand, Google's API failed silently with
with my fake domain name, and I had to used 'localhost' to test login with
Google and 'catalogapplication.com' to test it with Facebook.
"""
if __name__ == '__main__':
    app.secret_key = 'this_is_the_wildcat'
    app.debug = True
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
