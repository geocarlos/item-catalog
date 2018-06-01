from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import time

from database_setup import Category, Base, Item

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

## Dictionaries to populate objects
categories = [
    {'name': 'football'},
    {'name': 'volleyball'},
    {'name': 'tennis'},
    {'name': 'skating'},
    {'name': 'biking'}
]

items = [
    {'name': 'football cleats',
    'description': 'This is about shoes for English football, rather than American football.',
    'category': 0
    },
    {'name': 'net',
    'description': 'The net that separates the two volleyball teams competing agains one another.',
    'category': 1
    },
    {'name': 'racket',
    'description': 'The tool used by the players to hit the bal.',
    'category': 2
    },
    {'name': 'pedal',
    'description': 'Very importat to have a comfortable biking experience, therefore, the pedals are very important.',
    'category': 4
    },
    {'name': 'Shinguards',
    'description': 'Prevent having your shinbone broken when fighting for the ball.',
    'category': 0
    },
]

## List to hold the Category objects, so that they can be used when
## creating the Item objects in the for loop
cats = []

for i in range(0, len(categories)):
    cats.append(Category(name=categories[i]['name']))
    session.add(cats[i])
    session.commit()

for item in items:
    print cats[item['category']].name
    session.add(Item(
        name=item['name'],
        description=item['description'],
        category=cats[item['category']]
    ))
    session.commit()
    time.sleep(2) # So I can test "Latest Added Items"

print('Added items')
