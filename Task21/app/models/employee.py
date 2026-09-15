from pydantic import BaseModel, Field


class EmployeeCreate(BaseModel):
    name: str
    email: str
    department: str


class Employee(BaseModel):
    id: str
    name: str
    email: str
    department: str