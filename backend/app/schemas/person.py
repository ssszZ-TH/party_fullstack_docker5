from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Schema สำหรับสร้าง person
class PersonCreate(BaseModel):
    username: str
    email: str
    password: str
    personal_id_number: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    nick_name: Optional[str] = None
    birth_date: str
    gender_type_id: Optional[int] = None
    marital_status_type_id: Optional[int] = None
    country_id: Optional[int] = None
    height: int
    weight: int
    racial_type_id: Optional[int] = None
    income_range_id: Optional[int] = None
    about_me: Optional[str] = None

# Schema สำหรับอัปเดต person
class PersonUpdate(BaseModel):
    personal_id_number: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    nick_name: Optional[str] = None
    birth_date: Optional[str] = None
    gender_type_id: Optional[int] = None
    marital_status_type_id: Optional[int] = None
    country_id: Optional[int] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    racial_type_id: Optional[int] = None
    income_range_id: Optional[int] = None
    about_me: Optional[str] = None

# Schema สำหรับแสดงผล person
class PersonOut(BaseModel):
    id: int
    username: str
    email: str
    personal_id_number: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    nick_name: Optional[str] = None
    birth_date: str
    gender_type_id: Optional[int] = None
    marital_status_type_id: Optional[int] = None
    country_id: Optional[int] = None
    height: int
    weight: int
    racial_type_id: Optional[int] = None
    income_range_id: Optional[int] = None
    about_me: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True