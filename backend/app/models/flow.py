from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Flow(Base):
    __tablename__ = 'flows'
    flow_id = Column(String, primary_key=True)
    flow_data = Column(Text)
    flow_name = Column(String)
