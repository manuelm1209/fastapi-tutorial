from pydantic import BaseModel
from sqlmodel import SQLModel, Field

# Base model for Customer with common attributes
class CustomerBase(SQLModel):
    name: str = Field(default=None)  # Customer's name
    description: str | None = Field(default=None)  # Optional description of the customer
    email: str = Field(default=None)  # Customer's email address
    age: int = Field(default=None)  # Customer's age
    
# Model for creating a new customer, inherits from CustomerBase
class CustomerCreate(CustomerBase):
    pass

# Model for updating an existing customer, inherits from CustomerBase
class CustomerUpdate(CustomerBase):
    pass

# Customer model representing a database table
class Customer(CustomerBase, table=True):
    id: int | None = Field(default=None, primary_key=True)  # Primary key ID for the customer
    
# Model representing a financial transaction
class Transaction(BaseModel):
    id: int  # Unique identifier for the transaction
    ammount: int  # Amount of money involved in the transaction
    description: str  # Description of the transaction
    
# Model representing an invoice containing multiple transactions
class Invoice(BaseModel):
    id: int  # Unique identifier for the invoice
    customer: Customer  # Customer associated with the invoice
    transactions: list[Transaction]  # List of transactions included in the invoice
    total: int  # Total amount of the invoice
    
    @property
    def ammount_total(self):
        """Calculate the total amount from all transactions."""
        return sum(transaction.ammount for transaction in self.transactions)
