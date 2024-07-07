from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from db import SessionLocal, engine, Base
from models import User
import schemas
import auth  

# Create all tables in the database which are defined by Base's subclasses
Base.metadata.create_all(bind=engine)

# Create a FastAPI instance
app = FastAPI()

# Dependency function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()e

# Endpoint for user registration
@app.post("/register/", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
# Check if the user already exists
    db_user = auth.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    # Create a new user
    new_user = auth.create_user(db)
    # Return 201 Created and the new user data
    return new_user, status.HTTP_201_CREATED

# Endpoint for user login to get an access token
@app.post("/login/", response_model=auth.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: auth.OAuth2PasswordRequestForm = Depends()):
    # Authenticate the user
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Define the expiration time for the access token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Create a new access token
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Example endpoint for getting user's own contacts
@app.get("/contacts/", response_model=List[schemas.Contact])
def read_user_contacts(current_user: User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    contacts = db.query(schemas.Contact).filter(schemas.Contact.owner_id == current_user.id).all()
    return contacts

# Example endpoint for creating a contact
@app.post("/contacts/", response_model=schemas.Contact)
def create_contact(contact: schemas.ContactCreate, current_user: User = Depends(auth.get_current_active_user), db: Session = Depends(get_db)):
    new_contact = schemas.Contact(**contact.dict(), owner_id=current_user.id)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    
    # Return 201 Created and the new contact data
    return new_contact, status.HTTP_201_CREATED

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
