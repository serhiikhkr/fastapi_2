from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.emtity.models import Contact
from src.schemas.contact import ContactCreate


def get_contacts(limit: int, offset: int, db: Session):
    query = select([Contact]).limit(limit).offset(offset)
    contacts = db.execute(query).fetchall()
    return contacts


def get_contact(contact_id: int, db: Session):
    query = select(Contact).filter(Contact.id == contact_id)
    contact = db.execute(query).scalar_one_or_none()
    return contact


def create_contact(body: ContactCreate, db: Session):
    try:
        contact = Contact(**body.model_dump())
        db.add(contact)
        db.commit()
        return contact
    except Exception:
        raise HTTPException(status_code=400, detail="Помилка створення контакту")


def update_contact(contact_id: int, body: ContactCreate, db: Session):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Контакт не знайдено")

    contact_data = vars(body)
    for field, value in contact_data.items():
        setattr(contact, field, value)

    db.commit()
    db.refresh(contact)

    return contact


def delete_contact(contact_id: int, db: Session):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Контакт не знайдено")
    db.delete(contact)
    db.commit()
    return {"message": "Контакт видалено успішно"}


def search_contact(query: str, db: Session):
    contacts = (
        db.query(Contact)
        .filter(
            (Contact.first_name.ilike(f"%{query}%")) |
            (Contact.last_name.ilike(f"%{query}%")) |
            (Contact.email.ilike(f"%{query}%"))
        )
        .all()
    )
    return contacts


def upcoming_birthdays(db: Session):
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    birthdays = (
        db.query(Contact)
        .filter(
            (Contact.birthday >= today) &
            (Contact.birthday <= next_week)
        )
        .order_by(Contact.birthday)
        .all()
    )
    return birthdays
