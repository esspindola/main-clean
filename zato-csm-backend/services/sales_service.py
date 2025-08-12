from fastapi import HTTPException
from typing import List

from repositories.sales_repositories import SalesRepository
from product_service import

class SalesService:
    def __init__(self, sales_repo: SalesRepository):
        self.sales_repo = sales_repo

    def create_sale(self, items: List[dict], total: float,
                    paymentMethod: str, user: dict, status: str='completed'):

        if not items:
            raise HTTPException(status_code=400, detail="Items are required")
        if total <= 0:
            raise HTTPException(status_code=400, detail="Total must be positive")
        if not paymentMethod:
            raise HTTPException(status_code=400, detail="Payment method is required")

        user_id = user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User not found")



        return self.sales_repo.create_sale(
            items,
            total,
            paymentMethod,
            user_id,
            status
        )