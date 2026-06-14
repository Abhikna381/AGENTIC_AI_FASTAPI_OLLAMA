from pydantic import BaseModel, EmailStr
from typing import Optional


class EmployeeBase(BaseModel):
    name: str
    email: EmailStr



class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(EmployeeBase):
    pass
   


class EmployeeOut(EmployeeBase): # employee output schema, used for response models
    id: int 

    class Config: # 'orm_mode' has been renamed to 'from_attributes'
        from_attributes = True # object relational mapping mode, allows Pydantic to work with ORM objects