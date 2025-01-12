# from fastapi import APIRouter
# from ..models import Customer

# router = APIRouter()

# @router.post("/customers", response_model=Customer)    
# async def create_customer(customer_data: CustomerCreate):
#     customer = Customer.model_validate(customer_data.model_dump())
#     customer.id = len(db_customers)
#     db_customers.append(customer)
#     return customer

# @router.get("/customers", response_model = list[Customer])
# async def list_customer():
#     return db_customers