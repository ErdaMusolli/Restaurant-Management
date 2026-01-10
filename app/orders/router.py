from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from . import crud, schemas
from app.auth.oauth2 import get_current_user
from app.orders.models import Order

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=schemas.OrderRead)
async def create_order(
    order: schemas.OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await crud.create_order(db, order, current_user.id)

@router.get("/", response_model=List[schemas.OrderRead])
async def get_orders(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role == "admin":
        return await crud.get_all_orders(db)
    elif current_user.role == "manager":
        if not current_user.restaurant_id:
            raise HTTPException(status_code=403, detail="Manager not assigned to a restaurant")
        return await crud.get_orders_by_restaurant(db, current_user.restaurant_id)
    else:
        return await crud.get_orders_by_user(db, current_user.id)

@router.get("/my-orders", response_model=List[schemas.OrderRead])
async def get_my_orders(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    return await crud.get_orders_by_user(db, current_user.id)

@router.patch("/{order_id}/status", response_model=schemas.OrderRead)
async def update_order_status(
    order_id: int,
    status_update: schemas.OrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_order = await crud.get_order_by_id(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role == "manager":
        if db_order.restaurant_id != current_user.restaurant_id:
            raise HTTPException(status_code=403, detail="Cannot update orders of other restaurants")
    return await crud.update_order_status(db, db_order, status_update)

@router.delete("/{order_id}")
async def delete_order(order_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete orders")
    db_order = await crud.get_order_by_id(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    await crud.delete_order(db, db_order)
    return {"detail": "Order deleted successfully"}
