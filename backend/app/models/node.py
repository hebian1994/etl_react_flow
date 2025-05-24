from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Node(Base):
    __tablename__ = 'nodes'
    id = Column(String, primary_key=True)
    type = Column(String)
    created_at = Column(String)

class Dependency(Base):
    __tablename__ = 'dependencies'
    source = Column(String, primary_key=True)
    target = Column(String, primary_key=True) 