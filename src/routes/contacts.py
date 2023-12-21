from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import contacts as repository_contacts
from src.schemas.contact import ContactResponse, ContactCreate

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get('/', response_model=ContactResponse)
def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    contacts = repository_contacts.get_contacts(limit, offset, db)
    if not contacts:
        return {"message": "База пуста"}
    return contacts


@router.get('/search', response_model=ContactResponse)
def search_contact(query: str = Query(..., min_length=1, description="Пошуковий запит (ім'я, прізвище або email)"),
                   db: Session = Depends(get_db)):
    contacts = repository_contacts.search_contact(query, db)
    if not contacts:
        return "Ничего не найдено"
    return contacts


@router.get('/birthdays')
def upcoming_birthdays(db: Session = Depends(get_db)):
    birthdays = repository_contacts.upcoming_birthdays(db)
    if not birthdays:
        return {"message": "No BD"}
    return birthdays


@router.get('/{contact_id}', response_model=ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = repository_contacts.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=404, detail="Контакт не найден")
    return contact


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(body: ContactCreate, db: Session = Depends(get_db)):
    new_contact = repository_contacts.create_contact(body, db)
    return new_contact


@router.put('/{contact_id}', response_model=ContactResponse)
def update_contact(contact_id: int, body: ContactCreate, db: Session = Depends(get_db)):
    updated_contact = repository_contacts.update_contact(contact_id, body, db)
    return updated_contact


@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    delete_report = repository_contacts.delete_contact(contact_id, db)
    return delete_report
