from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database_setup import Base, Category, Item

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db',connect_args={'check_same_thread':False},
                    poolclass=StaticPool)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catalog')
def catalog():
    categories = session.query(Category).all()
    items = session.query(Item).all()
    return render_template('catalog.html', categories=categories)

@app.route('/catalog/<category>/items')
def category(category):
    return 'A list of items within the category'

@app.route('/catalog/<category>/<item>')
def item(category, item):
    return 'The details of the given item'

@app.route('/catalog/add')
def add_item():
    return 'Page to add new item'

@app.route('/catalog/<item>/edit')
def edit_item(item):
    return 'Page to edit item'

@app.route('/catalog/<item>/delete')
def delete_item(item):
    return 'Page to delete item'

### JSON API ###
@app.route('/catalog.json')
def catalogJSON():
    categories = session.query(Category).all()
    items = session.query(Item).all()
    Categories=[c.serialize for c in categories]
    Items=[i.serialize for i in items]
    for cat in Categories:
        cat['items'] = []
        for item in Items:
            if cat['id'] == item['category_id']:
                cat['items'].append(item)

    return  jsonify(Categories=Categories)

### JSON API ENDS ###

if __name__ == '__main__':
    app.secret_key = 'this_is_the_wildcat'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
