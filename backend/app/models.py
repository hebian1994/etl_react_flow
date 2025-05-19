
# Define Models
# models.py

from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Flow(Base):
    __tablename__ = 'flows'
    flow_id = Column(String, primary_key=True)
    flow_data = Column(Text)


class NodeConfig(Base):
    __tablename__ = 'node_configs'
    flow_id = Column(String, primary_key=True)
    node_id = Column(String, primary_key=True)
    config_name = Column(String, primary_key=True)
    config_param = Column(String)


class Node(Base):
    __tablename__ = 'nodes'
    id = Column(String, primary_key=True)
    type = Column(String)
    created_at = Column(String)


class Dependency(Base):
    __tablename__ = 'dependencies'
    source = Column(String, primary_key=True)
    target = Column(String, primary_key=True)
