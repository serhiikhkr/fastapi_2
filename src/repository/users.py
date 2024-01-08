from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.emtity.models import Users
from src.schemas.users import UserSchema


def get_user_by_email(email: str, db: Session = Depends(get_db)):
    """
    The get_user_by_email function takes an email address and returns the user associated with that email.
    If no such user exists, it returns None.

    :param email: str: Specify the type of the email parameter
    :param db: Session: Pass the database session into the function
    :return: A single user object
    :doc-author: Trelent
    """
    stmt = select(Users).filter_by(email=email)
    user = db.execute(stmt).scalar_one_or_none()
    return user


def create_user(body: UserSchema, db: Session = Depends(get_db)):
    """
    The create_user function creates a new user in the database.

    :param body: UserSchema: Validate the request body
    :param db: Session: Get the database session
    :return: The newly created user object
    :doc-author: Trelent
    """
    new_user = Users(**body.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_token(user: Users, token: str | None, db: Session):
    """
    The update_token function updates the refresh token for a user in the database.
        Args:
            user (Users): The User object to update.
            token (str | None): The new refresh token to store in the database. If None, then no change is made to this field.
                This is useful if you want to clear out an existing value but don't have a new one yet, or if you just want
                to update other fields and leave this one alone.

    :param user: Users: Specify the type of user that is being passed in
    :param token: str | None: Define the type of the token parameter
    :param db: Session: Access the database
    :return: None
    :doc-author: Trelent
    """
    user.refresh_token = token
    db.commit()


def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.


    :param email: str: Specify the email of the user to be confirmed
    :param db: Session: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    user = get_user_by_email(email, db)
    user.confirmed = True
    db.commit()
