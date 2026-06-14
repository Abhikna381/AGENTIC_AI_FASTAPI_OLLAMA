from pydantic import BaseModel, Field, StrictInt, StrictStr
from typing import Optional


class Employee(BaseModel):
    id: StrictInt = Field(..., gt=0, title="Employee ID", description="The unique identifier for the employee")
    name: StrictStr = Field(..., min_length=3, max_length=30, title="Employee Name", description="The name of the employee")
    age: Optional[StrictInt] = Field(default = None, gt=0, le=150, title="Employee Age", description="The age of the employee (optional)")