
# db.py
from models import Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
# todo: 需要修改为相对路径
DATABASE_FILE = r'D:\prj_py\etl_dask\backend\app\config.db'


DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 多线程支持
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # 初始化数据库时调用（只需调用一次）


# def init_db():
#     Base.metadata.create_all(bind=engine)
