
from fastapi import APIRouter, Form, UploadFile, File,Depends, HTTPException, Body, Request
from typing import List, Optional
import os

from repositories.product_repositories import ProductRepository
from utils.dependencies import get_current_user
from config.database import get_db_connection

from services.product_service import ProductService
from utils.timezone_utils import get_user_timezone_from_request

router = APIRouter(prefix="/api/products", tags=["products"])

"""
This function aims to create repository and service instance for this Route.
"""
def _get_product_service(db=Depends(get_db_connection)) -> ProductService:
    product_repo = ProductRepository(db) # postgres is default bank
    return ProductService(product_repo)


@router.post("/")
def create_product(request: Request,
                   name: str = Form(...),
                   description: str = Form(...),
                   price: float = Form(...),
                   stock: int = Form(...),
                   category: str = Form(...),
                   images: List[UploadFile] = File(None),
                   current_user=Depends(get_current_user),
                   product_service=Depends(_get_product_service)
                   ):
    user_timezone = get_user_timezone_from_request(request)
    product = product_service.create_product(name, description, price, stock, category, images)
    return {"success": True, "message": "Product created successfully", "product": product}

@router.get("/{product_id}")
def get_product(product_id: int,
                current_user=Depends(get_current_user),
                product_service=Depends(_get_product_service)):
    product = product_service.get_product(product_id)
    return {"success": True, "message": "Product found", "product": product}

@router.put("/{product_id}")
def update_product(product_id: int,
                   updates:dict = Body(...),
                   current_user=Depends(get_current_user),
                   product_service=Depends(_get_product_service)):
    product_updated = product_service.update_product(product_id, updates)
    return {"success": True, "message": "Product updated successfully", "product": product_updated}

@router.delete("/{product_id}")
def delete_product(product_id: int,
                   current_user=Depends(get_current_user),
                   product_service=Depends(_get_product_service)):
    product = product_service.delete_product(product_id)
    return {"success": True, "message": "Product deleted successfully", "product": product}




