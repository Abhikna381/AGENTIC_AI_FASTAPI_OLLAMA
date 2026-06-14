from fastapi import FastAPI,HTTPException
# from models import Employee
from models_val import Employee
from typing import List 


employees_db: List[Employee] = []

app = FastAPI()


# 1. Read all Employees

@app.get("/employees", response_model=List[Employee])
def get_employees():
    return employees_db



# 2. Read Specific Employee

@app.get("/employees/{emp_id}", response_model=Employee)
def get_employee(emp_id: int):
    for index, employee in enumerate(employees_db):
        if employee.id == emp_id:
            return employees_db[index]
    raise HTTPException(status_code=404, detail="Employee not found")


# 3. Add an employee

@app.post("/add_employee", response_model=Employee)
def add_employee(new_emp: Employee):
    for employee in employees_db:
        if employee.id == new_emp.id:
            raise HTTPException(status_code=400, detail="Employee with this ID already exists")
    employees_db.append(new_emp)
    return new_emp



# 4. Update an employee

@app.put("/update_employee/{emp_id}", response_model=Employee)
def update_employee(emp_id: int, updated_emp: Employee):
    for index, employee in enumerate(employees_db):
        if employee.id == emp_id:
            employees_db[index] = updated_emp
            return updated_emp
    raise HTTPException(status_code=404, detail="Employee not found")


# 5. Delete an employee

@app.delete("/delete_employee/{emp_id}")
def delete_employee(emp_id: int):
    for index, employee in enumerate(employees_db):
        if employee.id == emp_id:
            del employees_db[index]
            return {"message": "Employee deleted successfully"}
    raise HTTPException(status_code=404, detail="Employee not found")
