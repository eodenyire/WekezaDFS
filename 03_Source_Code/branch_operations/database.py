from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Your Local MySQL Credentials
# Format: mysql+mysqlconnector://username:password@host/db_name
#SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:root@localhost/wekeza_dfs_db"

# Read from Environment Variable (for Docker) OR default to Localhost (for testing)
DB_HOST = os.getenv("DB_HOST", "localhost")
SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://root:root@{DB_HOST}/wekeza_dfs_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()