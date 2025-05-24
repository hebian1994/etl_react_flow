from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class NodeConfig(Base):
    __tablename__ = 'node_configs'
    flow_id = Column(String, primary_key=True)
    node_id = Column(String, primary_key=True)
    config_name = Column(String, primary_key=True)
    config_param = Column(String)


class NodeSchema(Base):
    __tablename__ = 'node_schemas'
    node_id = Column(String, primary_key=True)
    node_schema = Column(String)
    created_at = Column(String)
    updated_at = Column(String)


class NodeConfigStatus(Base):
    __tablename__ = 'node_config_status'
    flow_id = Column(String, primary_key=True)
    node_id = Column(String, primary_key=True)
    config_status = Column(String)
    created_at = Column(String)
    updated_at = Column(String)


class NodeConfigOptions(Base):
    __tablename__ = 'node_config_options'
    node_type = Column(String, primary_key=True)
    node_config_option = Column(String)
    created_at = Column(String)
    updated_at = Column(String)
