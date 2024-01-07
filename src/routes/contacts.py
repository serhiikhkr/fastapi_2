from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from fastapi_limiter import FastAPILimiter

from src.database.db import get_db
from src.emtity.models import Users
from src.repository import contacts as repository_contacts
from src.schemas.contact import ContactResponse, ContactCreate, ContactsResponse
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get('/', response_model=ContactsResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0), db: Session = Depends(get_db),
                 user: Users = Depends(auth_service.get_current_user)):
    contacts = repository_contacts.get_contacts(limit, offset, db, user)
    if not contacts:
        return []
    return {"contacts": contacts}


@router.get('/search', response_model=ContactsResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def search_contact(query: str = Query(..., min_length=1, description="Пошуковий запит (ім'я, прізвище або email)"),
                   db: Session = Depends(get_db), user: Users = Depends(auth_service.get_current_user)):
    contacts = repository_contacts.search_contact(query, db, user)
    if not contacts:
        return "Ничего не найдено"
    return {"contacts": contacts}


@router.get('/birthdays', description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def upcoming_birthdays(db: Session = Depends(get_db), user: Users = Depends(auth_service.get_current_user)):
    birthdays = repository_contacts.upcoming_birthdays(db, user)
    if not birthdays:
        return {"message": "No BD"}
    return birthdays


@router.get('/{contact_id}', response_model=ContactResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def get_contact(contact_id: int, db: Session = Depends(get_db), user: Users = Depends(auth_service.get_current_user)):
    contact = repository_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=404, detail="Контакт не найден")
    return contact


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             description='No more than 10 requests per minute',
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def create_contact(body: ContactCreate, db: Session = Depends(get_db),
                   user: Users = Depends(auth_service.get_current_user)):
    new_contact = repository_contacts.create_contact(body, db, user)
    return new_contact


@router.put('/{contact_id}', response_model=ContactResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def update_contact(contact_id: int, body: ContactCreate, db: Session = Depends(get_db),
                   user: Users = Depends(auth_service.get_current_user)):
    updated_contact = repository_contacts.update_contact(contact_id, body, db, user)
    return updated_contact


@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT,
               description='No more than 10 requests per minute',
               dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def delete_contact(contact_id: int, db: Session = Depends(get_db),
                   user: Users = Depends(auth_service.get_current_user)):
    delete_report = repository_contacts.delete_contact(contact_id, db, user)
    return delete_report
