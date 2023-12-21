from pydantic import BaseModel, EmailStr

from datetime import date


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: date
    additional_data: str = None


class ContactCreate(ContactBase):
    pass


class ContactResponse(ContactBase):
    id: int

    class Config:
        from_attributes = True
