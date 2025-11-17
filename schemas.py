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
from typing import Optional
from datetime import datetime

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

# Crowdfunding schemas

class Campaign(BaseModel):
    """
    Campaign collection schema
    Collection name: "campaign"
    """
    title: str = Field(..., description="Campaign title")
    description: str = Field(..., description="Why you're raising funds")
    goal_amount: float = Field(..., gt=0, description="Total amount to raise")
    max_supporters: Optional[int] = Field(100, gt=0, description="Maximum number of supporters")
    deadline: Optional[datetime] = Field(None, description="Optional deadline for the campaign")

class Contribution(BaseModel):
    """
    Contribution collection schema
    Collection name: "contribution"
    """
    name: str = Field(..., description="Supporter's name")
    email: EmailStr = Field(..., description="Supporter's email")
    amount: float = Field(..., gt=0, description="Contribution amount in dollars")
    message: Optional[str] = Field(None, description="A short note from the supporter")
    is_public: bool = Field(True, description="Whether to show their name/messages publicly")
