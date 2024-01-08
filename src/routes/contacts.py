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
    """
    The get_contacts function returns a list of contacts.

    :param limit: int: Limit the number of contacts returned
    :param ge: Set a minimum value for the limit parameter
    :param le: Limit the number of contacts returned
    :param offset: int: Skip a number of records
    :param ge: Set a minimum value for the parameter
    :param db: Session: Get the database session
    :param user: Users: Get the current user
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = repository_contacts.get_contacts(limit, offset, db, user)
    if not contacts:
        return []
    return {"contacts": contacts}


@router.get('/search', response_model=ContactsResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def search_contact(query: str = Query(..., min_length=1, description="Пошуковий запит (ім'я, прізвище або email)"),
                   db: Session = Depends(get_db), user: Users = Depends(auth_service.get_current_user)):
    """
    The search_contact function allows you to search for contacts by name, surname or email.

    :param query: str: Pass the search query to the function
    :param min_length: Set the minimum length of the query string
    :param description: Add a description to the parameter
    :param прізвище або email)&quot;): Describe the parameter in the documentation
    :param db: Session: Pass the database session to the function
    :param user: Users: Get the user id from the jwt token
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = repository_contacts.search_contact(query, db, user)
    if not contacts:
        return "Ничего не найдено"
    return {"contacts": contacts}


@router.get('/birthdays', description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def upcoming_birthdays(db: Session = Depends(get_db), user: Users = Depends(auth_service.get_current_user)):

    """
    The upcoming_birthdays function returns a list of contacts with upcoming birthdays.

    :param db: Session: Get a database session
    :param user: Users: Get the current user
    :return: A list of contacts whose birthday is in the next 30 days
    :doc-author: Trelent
    """
    birthdays = repository_contacts.upcoming_birthdays(db,user)
    if not birthdays:
        return {"message": "No BD"}
    return birthdays


@router.get('/{contact_id}', response_model=ContactResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def get_contact(contact_id: int, db: Session = Depends(get_db), user: Users = Depends(auth_service.get_current_user)):

    """
    The get_contact function returns a contact by its ID.

    :param contact_id: int: Specify the type of data that will be passed to the function
    :param db: Session: Pass the database session to the function
    :param user: Users: Get the current user
    :return: The contact with the specified id
    :doc-author: Trelent
    """
    contact = repository_contacts.get_contact(contact_id,db, user)
    if contact is None:
        raise HTTPException(status_code=404, detail="Контакт не найден")
    return contact


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             description='No more than 10 requests per minute',
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def create_contact(body: ContactCreate, db: Session = Depends(get_db),
                   user: Users = Depends(auth_service.get_current_user)):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactCreate: Get the contact details from the request body
    :param db: Session: Pass the database session to the repository layer
    :param user: Users: Get the current user
    :return: A contact object
    :doc-author: Trelent
    """
    new_contact = repository_contacts.create_contact(body, db, user)
    return new_contact


@router.put('/{contact_id}', response_model=ContactResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def update_contact(contact_id: int, body: ContactCreate, db: Session = Depends(get_db),
                   user: Users = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
        The function takes three arguments:
            - contact_id: int, the id of the contact to be updated.
            - body: ContactCreate, an object containing all of the fields that can be updated for a given user's contacts.  This is defined in schemas/contacts_schemas.py and includes first name, last name, email address and phone number (all optional).  It also includes an optional list of tags associated with this particular contact (also defined in schemas/tags_schemas).
            - db: Session =

    :param contact_id: int: Specify the contact to be updated
    :param body: ContactCreate: Update the contact
    :param db: Session: Pass the database session to the repository
    :param user: Users: Get the current user from the database
    :return: The updated contact
    :doc-author: Trelent
    """
    updated_contact = repository_contacts.update_contact(contact_id, body, db, user)
    return updated_contact


@router.delete('/{contact_id}', status_code=status.HTTP_204_NO_CONTENT,
               description='No more than 10 requests per minute',
               dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def delete_contact(contact_id: int, db: Session = Depends(get_db),
                   user: Users = Depends(auth_service.get_current_user)):
    """
    The delete_contact function deletes a contact from the database.
        Args:
            contact_id (int): The id of the contact to be deleted.
            db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).
            user (Users, optional): User object containing information about the current user's session.  Defaults to Depends(auth_service.get_current_user).

    :param contact_id: int: Specify the contact id of the contact to be deleted
    :param db: Session: Pass the database session to the repository function
    :param user: Users: Get the user id of the current user
    :return: A dict with the following keys:
    :doc-author: Trelent
    """
    delete_report = repository_contacts.delete_contact(contact_id, db, user)
    return delete_report
