# Import necessary modules from SQLAlchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Create a base class for declarative class definitions
Base = declarative_base()

# Define the User model
class User(Base):
    __tablename__ = 'users'  # Name of the table in the database

    # Define columns for the users table
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True) 
    hashed_password = Column(String)  
