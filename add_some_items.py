from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import time

from database_setup import Category, Base, Item

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

"""
    This is script is intended to add some initial data
    to the database for testing.
"""

# Dictionaries to populate objects
categories = [
    {'name': 'football', 'user_id': 1},
    {'name': 'volleyball', 'user_id': 1},
    {'name': 'tennis', 'user_id': 1},
    {'name': 'skating', 'user_id': 1},
    {'name': 'biking', 'user_id': 1}
]

items = [
    {'name': 'football cleats',
     'description': '''This is about shoes for English football,
     rather than American football.''',
     'category': 0,
     'user_id': 1
     },
    {'name': 'net',
     'description': '''The net that separates the two volleyball
     teams competing agains one another.''',
     'category': 1,
     'user_id': 2
     },
    {'name': 'racket',
     'description': 'The tool used by the players to hit the bal.',
     'category': 2,
     'user_id': 1
     },
    {'name': 'pedal',
     'description': '''Very importat to have a comfortable biking experience,
     therefore, the pedals are very important.''',
     'category': 4,
     'user_id': 1
     },
    {'name': 'Shinguards',
     'description': '''Prevent having your shinbone broken when
     fighting for the ball.''',
     'category': 0,
     'user_id': 2
     },
]

# List to hold the Category objects, so that they can be used when
# creating the Item objects in the for loop
cats = []

for i in range(0, len(categories)):
    cats.append(Category(name=categories[i]['name'],
                         user_id=categories[i]['user_id']))
    session.add(cats[i])
    session.commit()

for item in items:
    print cats[item['category']].name
    session.add(Item(
        name=item['name'],
        description=item['description'],
        category=cats[item['category']],
        user_id=item['user_id']
    ))
    session.commit()
    time.sleep(2)  # So I can test "Latest Added Items"

print('Added items')
