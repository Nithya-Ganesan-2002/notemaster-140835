# All FastAPI endpoints for user registration, auth, and note CRUD.

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from src.api import models
from src.api.db import get_db, User, Note
from src.api.auth import (
    get_password_hash, authenticate_user, create_access_token
)

from jose import JWTError, jwt

import os

SECRET_KEY = os.getenv("SECRET_KEY", "CHANGEME_SECRET")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# PUBLIC_INTERFACE
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Gets the user for a given JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

router = APIRouter()

# --- Auth Endpoints ---

# PUBLIC_INTERFACE
@router.post("/auth/register", summary="Register a new user", tags=["auth"])
def register(user: models.UserCreate, db: Session = Depends(get_db)):
    """Register a new user and return their info."""
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=400, detail="Email already registered"
        )
    new_user = User(
        email=user.email,
        hashed_password=get_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email}

# PUBLIC_INTERFACE
@router.post("/auth/token", summary="Login and get access token", tags=["auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticate, returning JWT access token if correct."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Get current user
@router.get("/auth/me", response_model=models.UserRead, summary="Get current user", tags=["auth"])
def me(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's details."""
    return models.UserRead(id=current_user.id, email=current_user.email)

# --- Notes CRUD Endpoints ---

# PUBLIC_INTERFACE
@router.post("/notes/", response_model=models.NoteRead, summary="Create note", tags=["notes"])
def create_note(note: models.NoteCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Create a note for the current user."""
    db_note = Note(
        title=note.title,
        content=note.content,
        user_id=user.id
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

# PUBLIC_INTERFACE
@router.get("/notes/", response_model=List[models.NoteRead], summary="List notes", tags=["notes"])
def list_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Return all notes owned by the current user."""
    notes = db.query(Note).filter(Note.user_id == user.id).order_by(Note.updated_at.desc()).offset(skip).limit(limit).all()
    return notes

# PUBLIC_INTERFACE
@router.get("/notes/{note_id}", response_model=models.NoteRead, summary="Get note", tags=["notes"])
def get_note(note_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Get a single note."""
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

# PUBLIC_INTERFACE
@router.put("/notes/{note_id}", response_model=models.NoteRead, summary="Update note", tags=["notes"])
def update_note(note_id: int, note_update: models.NoteUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Update note (title/content) for current user."""
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if note_update.title is not None:
        note.title = note_update.title
    if note_update.content is not None:
        note.content = note_update.content
    db.commit()
    db.refresh(note)
    return note

# PUBLIC_INTERFACE
@router.delete("/notes/{note_id}", summary="Delete note", tags=["notes"])
def delete_note(note_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Delete a note for the current user."""
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return {"detail": "Note deleted"}
