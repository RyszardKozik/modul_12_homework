from sqlalchemy.orm import Session
from modul_12_homework import models, schemas, auth

# Read user by ID
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

# Read user by email
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# Create a new user
def create_new_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Update an existing user
def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        if user_update.email:
            user.email = user_update.email
        if user_update.password:
            user.hashed_password = auth.get_password_hash(user_update.password)
        db.commit()
        db.refresh(user)
        return user
    return None

# Delete a user
def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False

# Read contacts with pagination
def get_contacts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Contact).offset(skip).limit(limit).all()

# Create a new contact for a user
def create_user_contact(db: Session, contact: schemas.ContactCreate, user_id: int):
    db_contact = models.Contact(**contact.dict(), user_id=user_id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

# Read contact by ID
def get_contact(db: Session, contact_id: int):
    return db.query(models.Contact).filter(models.Contact.id == contact_id).first()

# Update a contact
def update_contact(db: Session, contact_id: int, contact_update: schemas.ContactUpdate):
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if contact:
        for var, value in vars(contact_update).items():
            setattr(contact, var, value) if value else None
        db.commit()
        db.refresh(contact)
        return contact
    return None

# Delete a contact
def delete_contact(db: Session, contact_id: int):
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
        return True
    return False
