from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users as repositories_users
from src.schemas.users import UserSchema, TokenSchema, UserResponse
from src.services.auth import auth_service

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(body: UserSchema, db: Session = Depends(get_db)):
    exist_user = repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = repositories_users.create_user(body, db)
    return new_user


@router.post("/login", response_model=TokenSchema)
def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = repositories_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    access_token = auth_service.create_access_token(data={"sub": user.email})
    refresh_tokens = auth_service.create_refresh_token(data={"sub": user.email})
    repositories_users.update_token(user, refresh_tokens, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenSchema)
def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                  db: Session = Depends(get_db)):
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
