import models, schemas, crud
from fastapi import FastAPI, HTTPException,Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from typing import List



Base.metadata.create_all(bind=engine) # create tables in the database if they don't exist



app = FastAPI()



# dependecy with the DB
def get_db():
    db = SessionLocal() # create a new database session
    try:
        yield db # yield the database session to the endpoint function, 
                 # allowing it to use the session for database operations  
    finally:
        db.close() # close the database session after the endpoint function is done, ensuring that resources are properly released



# enddpoints
# 1. Create an employee
@app.post("/employees/", response_model=schemas.EmployeeOut)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    return crud.create_employee(db=db, employee=employee)





# 2. get all employees
@app.get("/employees/", response_model=List[schemas.EmployeeOut])
def get_employees(db: Session = Depends(get_db)):
    return crud.get_employees(db=db)






# 3. get specific employee
@app.get("/employees/{emp_id}", response_model=schemas.EmployeeOut)
def get_employee(emp_id: int, db: Session = Depends(get_db)):
    employee = crud.get_employee(db=db, emp_id=emp_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee






# 4. update an employee
@app.put("/employees/{emp_id}", response_model=schemas.EmployeeOut)
def update_employee(emp_id: int, employee: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    updated_employee = crud.update_employee(db=db, emp_id=emp_id, employee=employee)
    if updated_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return updated_employee






# 5. delete an employee
@app.delete("/employees/{emp_id}", response_model= dict)
def delete_employee(emp_id: int,db: Session = Depends(get_db)):
    deleted_employee = crud.delete_employee(db=db, emp_id=emp_id)
    if deleted_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    # return deleted_employee
    return {"detail": "Employee deleted successfully"}

