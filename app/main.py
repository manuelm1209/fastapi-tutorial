import zoneinfo
from fastapi import FastAPI, HTTPException, status
from datetime import datetime
from .db import SessionDep, create_all_tables
from .models import Customer, CustomerCreate, CustomerUpdate, Invoice, Transaction
from sqlmodel import select

app = FastAPI(lifespan=create_all_tables)

country_timezones = {
    "CO": "America/Bogota",
    "MX": "America/Mexico_City",
    "AR": "America/Argentina/Buenos_Aires",
    "BR": "America/Sao_Paulo",
    "PE": "America/Lima",
}

@app.get("/")
async def root():
    return {"message": "Hola, Manuel!"}

@app.get("/time/{iso_code}")
async def time(iso_code: str):
    iso = iso_code.upper()
    timezone_str = country_timezones.get(iso)
    tz = zoneinfo.ZoneInfo(timezone_str)
    return {"iso_code": iso_code.upper(),
            "country_zone": timezone_str,
            "time": datetime.now(tz)}
    
db_customers: list[Customer] = []

@app.post("/customers", response_model=Customer)    
async def create_customer(customer_data: CustomerCreate, session: SessionDep):
    customer = Customer.model_validate(customer_data.model_dump())
    session.add(customer)
    session.commit()
    session.refresh(customer)
    ### Without DB
    # customer.id = len(db_customers)
    # db_customers.append(customer)
    return customer


@app.get("/customer/{customer_id}", response_model=Customer)
async def read_customer(customer_id:int, session: SessionDep):
    customer_db = session.get(Customer, customer_id)
    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer doesn't exist")
    return customer_db


@app.patch("/customer/{customer_id}", response_model=Customer, status_code=status.HTTP_201_CREATED)
async def update_customer(customer_id:int, customer_data: CustomerUpdate, session: SessionDep):
    customer_db = session.get(Customer, customer_id)
    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer doesn't exist")
    customer_data_dict = customer_data.model_dump(exclude_unset=True)
    customer_db.sqlmodel_update(customer_data_dict)
    session.add(customer_db)
    session.commit()
    session.refresh(customer_db)
    return customer_db


@app.delete("/customer/{customer_id}")
async def delete_customer(customer_id:int, session: SessionDep):
    customer_db = session.get(Customer, customer_id)
    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer doesn't exist")
    session.delete(customer_db)
    session.commit()
    return {"detail": "ok"}


@app.get("/customers", response_model = list[Customer])
async def list_customer(session: SessionDep):
    return session.exec(select(Customer)).all()

@app.post("/transactions")
async def create_transaction(customer_data: Transaction):
    return customer_data

@app.post("/invoices")    
async def create_invoice(customer_data: Invoice):
    return customer_data