from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.emtity.models import Contact, Users
from src.schemas.contact import ContactCreate


def get_contacts(limit: int, offset: int, db: Session, user: Users):
    contacts = db.query(Contact).filter_by(user=user).offset(offset).limit(limit).all()
    if not contacts:
        return {"message": "Список контактов пуст"}
    return contacts


def get_contact(contact_id: int, db: Session, user: Users):
    query = select(Contact).filter_by(id=contact_id, user=user)
    contact = db.execute(query).scalar_one_or_none()
    return contact


def create_contact(body: ContactCreate, db: Session, user: Users):
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
    contact = db.query(Contact).filter_by(id=contact_id, user=user).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Контакт не знайдено")
    db.delete(contact)
    db.commit()
    return {"message": "Контакт видалено успішно"}


def search_contact(query: str, db: Session, user: Users):
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
