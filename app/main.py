import zoneinfo
from fastapi import FastAPI, HTTPException, status
from datetime import datetime
from .db import SessionDep, create_all_tables
from .models import Customer, CustomerCreate, CustomerUpdate, Invoice, Transaction
from sqlmodel import select

# Initialize FastAPI application with database table creation on startup
app = FastAPI(lifespan=create_all_tables)

# Dictionary mapping country ISO codes to their respective time zones
country_timezones = {
    "CO": "America/Bogota",
    "MX": "America/Mexico_City",
    "AR": "America/Argentina/Buenos_Aires",
    "BR": "America/Sao_Paulo",
    "PE": "America/Lima",
}

@app.get("/")
async def root():
    """Root endpoint that returns a greeting message."""
    return {"message": "Hola, Manuel!"}

@app.get("/time/{iso_code}")
async def time(iso_code: str):
    """
    Get the current time in a specific country's time zone.
    
    Args:
        iso_code (str): The ISO code of the country.
    
    Returns:
        dict: A dictionary containing the ISO code, the corresponding time zone, and the current time.
    """
    iso = iso_code.upper()
    timezone_str = country_timezones.get(iso)
    tz = zoneinfo.ZoneInfo(timezone_str)
    return {
        "iso_code": iso_code.upper(),
        "country_zone": timezone_str,
        "time": datetime.now(tz)
    }

# In-memory customer storage for testing without a database
db_customers: list[Customer] = []

@app.post("/customers", response_model=Customer)
async def create_customer(customer_data: CustomerCreate, session: SessionDep):
    """
    Create a new customer and store it in the database.
    
    Args:
        customer_data (CustomerCreate): Customer data payload.
        session (SessionDep): Database session dependency.
    
    Returns:
        Customer: The created customer object.
    """
    customer = Customer.model_validate(customer_data.model_dump())
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer

@app.get("/customer/{customer_id}", response_model=Customer)
async def read_customer(customer_id: int, session: SessionDep):
    """
    Retrieve a customer by their ID.
    
    Args:
        customer_id (int): The ID of the customer.
        session (SessionDep): Database session dependency.
    
    Returns:
        Customer: The customer object if found, otherwise raises a 404 error.
    """
    customer_db = session.get(Customer, customer_id)
    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer doesn't exist")
    return customer_db

@app.patch("/customer/{customer_id}", response_model=Customer, status_code=status.HTTP_201_CREATED)
async def update_customer(customer_id: int, customer_data: CustomerUpdate, session: SessionDep):
    """
    Update an existing customer by their ID.
    
    Args:
        customer_id (int): The ID of the customer.
        customer_data (CustomerUpdate): The data to update.
        session (SessionDep): Database session dependency.
    
    Returns:
        Customer: The updated customer object.
    """
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
async def delete_customer(customer_id: int, session: SessionDep):
    """
    Delete a customer by their ID.
    
    Args:
        customer_id (int): The ID of the customer.
        session (SessionDep): Database session dependency.
    
    Returns:
        dict: A confirmation message upon successful deletion.
    """
    customer_db = session.get(Customer, customer_id)
    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer doesn't exist")
    session.delete(customer_db)
    session.commit()
    return {"detail": "ok"}

@app.get("/customers", response_model=list[Customer])
async def list_customer(session: SessionDep):
    """
    Retrieve a list of all customers.
    
    Args:
        session (SessionDep): Database session dependency.
    
    Returns:
        list[Customer]: A list of all customers in the database.
    """
    return session.exec(select(Customer)).all()

@app.post("/transactions")
async def create_transaction(customer_data: Transaction):
    """
    Create a transaction entry.
    
    Args:
        customer_data (Transaction): The transaction data.
    
    Returns:
        Transaction: The created transaction object.
    """
    return customer_data

@app.post("/invoices")
async def create_invoice(customer_data: Invoice):
    """
    Create an invoice entry.
    
    Args:
        customer_data (Invoice): The invoice data.
    
    Returns:
        Invoice: The created invoice object.
    """
    return customer_data
