from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.emtity.models import Contact, Users
from src.schemas.contact import ContactCreate


def get_contacts(limit: int, offset: int, db: Session, user: Users):
    """
    The get_contacts function returns a list of contacts for the user.
        Args:
            limit (int): The number of items to return.
            offset (int): The number of items to skip before returning results.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Set the offset of the query
    :param db: Session: Access the database
    :param user: Users: Filter the contacts by user
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter_by(user=user).offset(offset).limit(limit).all()
    if not contacts:
        return {"message": "Список контактов пуст"}
    return contacts


def get_contact(contact_id: int, db: Session, user: Users):
    """
    The get_contact function returns a contact from the database.
        Args:
            contact_id (int): The id of the contact to be retrieved.
            db (Session): A connection to the database.
            user (Users): The user who is requesting this information.

    :param contact_id: int: Specify the contact to retrieve
    :param db: Session: Pass the database session to the function
    :param user: Users: Ensure that the user is authorized to access this contact
    :return: The contact that matches the given id and user
    :doc-author: Trelent
    """
    query = select(Contact).filter_by(id=contact_id, user=user)
    contact = db.execute(query).scalar_one_or_none()
    return contact


def create_contact(body: ContactCreate, db: Session, user: Users):
    """
    The create_contact function creates a new contact in the database.
        Args:
            body (ContactCreate): The request body containing the details of the new contact.
            db (Session, optional): SQLAlchemy Session. Defaults to None.

    :param body: ContactCreate: Validate the data that is passed to the function
    :param db: Session: Access the database
    :param user: Users: Get the user_id from the token
    :return: A contact object
    :doc-author: Trelent
    """
    if not user:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    try:
        contact = Contact(**body.model_dump(), user=user)
        db.add(contact)
        db.commit()
        return contact
    except Exception:
        raise HTTPException(status_code=400, detail="Помилка створення контакту")


def update_contact(contact_id: int, body: ContactCreate, db: Session,
                   user: Users):
    """
    The update_contact function updates a contact in the database.
        Args:
            contact_id (int): The id of the contact to update.
            body (ContactCreate): The updated data for the Contact object.

    :param contact_id: int: Get the contact id from the url
    :param body: ContactCreate: Pass the data from the request body
    :param db: Session: Access the database
    :param user: Users: Get the user who is logged in
    :return: The updated contact
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter_by(id=contact_id, user=user).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Контакт не знайдено")

    contact_data = vars(body)
    for field, value in contact_data.items():
        setattr(contact, field, value)

    db.commit()
    db.refresh(contact)

    return contact


def delete_contact(contact_id: int, db: Session, user: Users):
    """
    The delete_contact function deletes a contact from the database.
        Args:
            contact_id (int): The id of the contact to delete.
            db (Session): A connection to the database.

    :param contact_id: int: Specify the id of the contact to be deleted
    :param db: Session: Get access to the database
    :param user: Users: Ensure that the user who is trying to delete a contact is the owner of this contact
    :return: A dictionary with the message key
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter_by(id=contact_id, user=user).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Контакт не знайдено")
    db.delete(contact)
    db.commit()
    return {"message": "Контакт видалено успішно"}


def search_contact(query: str, db: Session, user: Users):
    """
    The search_contact function searches for contacts in the database.
        Args:
            query (str): The search term to look for.
            db (Session): The database session object.
            user (Users): The user who is searching for a contact.

    :param query: str: Filter the contacts by first name, last name or email
    :param db: Session: Pass the database session to the function
    :param user: Users: Filter the query by user
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = (
        db.query(Contact)
        .filter_by(user=user)
        .filter(
            (Contact.first_name.ilike(f"%{query}%")) |
            (Contact.last_name.ilike(f"%{query}%")) |
            (Contact.email.ilike(f"%{query}%"))
        )
        .all()
    )
    return contacts


def upcoming_birthdays(db: Session, user: Users):
    """
    The upcoming_birthdays function returns a list of contacts whose birthdays are within the next week.

    :param db: Session: Pass in a database session, which is used to query the database
    :param user: Users: Filter the contacts by user
    :return: A list of contacts with birthdays
    :doc-author: Trelent
    """
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    birthdays = (
        db.query(Contact)
        .filter_by(user=user)
        .filter(
            (Contact.birthday >= today) &
            (Contact.birthday <= next_week)
        )
        .order_by(Contact.birthday)
        .all()
    )
    return birthdays
