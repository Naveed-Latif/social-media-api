from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from .config import settings


url = URL.create(
    drivername=settings.database_driver_name,
    username=settings.database_username,
    password=settings.database_password,
    host=settings.database_hostname,
    port=settings.database_port,
    database=settings.database_name,

)

engine = create_engine(url)
Session_local = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base = declarative_base()

def get_db():
    db = Session_local()
    try:
        yield db
    finally:
        db.close()
        
         
# while True:
#     try:
#         conn = psycopg2.connect(host='localhost', database='FastAPI', user='postgres',
#                                 password='Chichawatni@113', cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print("Database connection successful")
#         break
#     except Exception as error:
#         print("Database connection failed")
#         print("Error:", error)
#         time.sleep(2)