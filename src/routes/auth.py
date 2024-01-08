from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users as repositories_users
from src.schemas.users import UserSchema, TokenSchema, UserResponse, RequestEmail
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(body: UserSchema, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    The signup function creates a new user in the database.
        It takes in a UserSchema object, which is validated against the UserSchema class.
        If validation fails, an HTTPException is raised with status code 400 and error message &quot;Bad Request&quot;.

    :param body: UserSchema: Validate the data sent to the api
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the request
    :param db: Session: Pass the database session to the function
    :return: A dict with the user and a message
    :doc-author: Trelent
    """
    exist_user = repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = repositories_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}
    # return new_user


@router.post("/login", response_model=TokenSchema)
def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    The login function is used to authenticate a user.
        It takes in the username and password of the user, and returns an access token if successful.
        The access token can be used to make authenticated requests against protected endpoints.

    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: Session: Pass the database session to the function
    :return: A dictionary with three keys: access_token, refresh_token and token_type
    :doc-author: Trelent
    """
    user = repositories_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    access_token = auth_service.create_access_token(data={"sub": user.email})
    refresh_tokens = auth_service.create_refresh_token(data={"sub": user.email})
    repositories_users.update_token(user, refresh_tokens, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenSchema)
def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                  db: Session = Depends(get_db)):
    """
    The refresh_token function is used to refresh the access token.
        The function takes in a refresh token and returns an access_token,
        a new refresh_token, and the type of token (bearer).

    :param credentials: HTTPAuthorizationCredentials: Get the credentials from the request header
    :param db: Session: Pass the database session to the function
    :return: A dictionary containing the access_token, refresh_token and token type
    :doc-author: Trelent
    """
    token = credentials.credentials
    email = auth_service.decode_refresh_token(token)
    user = repositories_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        repositories_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = auth_service.create_access_token(data={"sub": email})
    refresh_tokens = auth_service.create_refresh_token(data={"sub": email})
    repositories_users.update_token(user, refresh_tokens, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    The confirmed_email function takes a token and db as parameters.
    The token is used to get the email from the auth_service.get_email_from_token function, which returns an email address.
    The user is then retrieved from the database using repositories_users.get_userbyemail, which returns a user object or None if no such user exists in the database.

    :param token: str: Get the email from the token
    :param db: Session: Get the database session
    :return: A message that the email has been confirmed
    :doc-author: Trelent
    """
    email = auth_service.get_email_from_token(token)
    user = repositories_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    repositories_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                  db: Session = Depends(get_db)):
    """
    The request_email function is used to send an email to the user with a link that will allow them
    to confirm their email address. The function takes in a RequestEmail object, which contains the
    email of the user who wants to confirm their account. It then checks if there is already a confirmed
    user with that email address, and if so returns an error message saying as much. If not, it sends
    an email containing a confirmation link.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the request
    :param db: Session: Get the database session
    :return: A message to the user
    :doc-author: Trelent
    """
    user = repositories_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}
