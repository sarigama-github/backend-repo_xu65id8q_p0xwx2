"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Real estate app schemas

class Property(BaseModel):
    """
    Real estate properties
    Collection: "property"
    """
    title: str
    description: str
    address: str
    city: str
    state: str
    country: str = "India"
    price: float
    bedrooms: int
    bathrooms: float
    area_sqft: int
    images: List[str] = []
    featured: bool = False
    status: str = Field("For Sale", description="For Sale | For Rent | Sold")

class Inquiry(BaseModel):
    """
    Contact/Inquiry submissions
    Collection: "inquiry"
    """
    name: str
    email: EmailStr
    phone: Optional[str] = None
    message: str
    property_id: Optional[str] = Field(None, description="If inquiring about a specific property")
