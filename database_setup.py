import sys
from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'name': self.name,
            'id': self.id
        }

class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(500))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'name': self.name,
            'description': self.description,
            'category_id': self.category_id,  
            'id': self.id
        }

engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
