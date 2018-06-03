from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database_setup import Base, Category, Item

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db', connect_args={'check_same_thread': False},
                       poolclass=StaticPool)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/catalog')
def catalog():
    categories = session.query(Category).all()
    # Items must be sorted by the time they were added
    # so that the "latest items" view will be as expected
    items = sorted(session.query(Item).all(),
                   key=lambda item: item.time_added, reverse=True)
    return render_template('catalog.html', categories=categories, items=items)

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
    return render_template('catalog.html', categories=categories, items=items, category=category)


@app.route('/catalog/<category>/<item>')
def item(category, item):
    item = session.query(Item).filter_by(name=item).one()
    return render_template('item.html', item=item)


@app.route('/catalog/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        newItem = Item(
            name=request.form['name'], description=request.form['description'], category_id=request.form['category'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('catalog'))
    else:
        categories = session.query(Category).all()
        return render_template('add_item.html', categories=categories)


@app.route('/catalog/<item>/edit', methods=['GET', 'POST'])
def edit_item(item):
    if request.method == 'POST':
        itemToEdit = session.query(Item).filter_by(id=request.form['id']).one()
        itemToEdit.name = request.form['name']
        itemToEdit.description = request.form['description']
        itemToEdit.category_id=request.form['category']
        category = session.query(Category).filter_by(id=itemToEdit.category_id)
        session.add(itemToEdit)
        session.commit()
        return redirect(url_for('item', category=category, item=itemToEdit.name))
    else:
        itemToEdit = session.query(Item).filter_by(name=item).one()
        categories = session.query(Category).all()
        return render_template('edit_item.html', categories=categories, item=itemToEdit)


@app.route('/catalog/<item>/delete')
def delete_item(item):
    return 'Page to delete item'


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


if __name__ == '__main__':
    app.secret_key = 'this_is_the_wildcat'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
