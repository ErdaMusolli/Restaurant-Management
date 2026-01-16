import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from . import crud, schemas
from app.database import get_db
from app.auth.oauth2 import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])
logger = logging.getLogger("app_logger")

@router.post("/", response_model=schemas.OrderRead)
async def create_order(
    order: schemas.OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create orders")
    db_order = await crud.create_order(db, order, current_user.id)
    logger.info(f"User {current_user.id} created order {db_order.id} for restaurant {db_order.restaurant_id}")
    return db_order

@router.get("/", response_model=List[schemas.OrderRead])
async def get_orders(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role == "admin":
        orders = await crud.get_all_orders(db)
    elif current_user.role == "manager":
        if not current_user.restaurant_id:
            raise HTTPException(status_code=403, detail="Manager has no restaurant assigned")
        orders = await crud.get_orders_by_restaurant(db, current_user.restaurant_id)
    else:
        raise HTTPException(status_code=403, detail="Only admin or manager can view orders")
    logger.info(f"User {current_user.id} viewed orders")
    return orders

@router.get("/me", response_model=List[schemas.OrderRead])
async def get_my_orders(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role != "user":
        raise HTTPException(status_code=403, detail="Only users can view their own orders")
    orders = await crud.get_orders_by_user(db, current_user.id)
    logger.info(f"User {current_user.id} viewed their own orders")
    return orders

@router.patch("/{order_id}/status", response_model=schemas.OrderRead)
async def update_order_status(order_id: int, status_update: schemas.OrderUpdate, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    db_order = await crud.get_order_by_id(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    if current_user.role == "manager" and db_order.restaurant_id != current_user.restaurant_id:
        raise HTTPException(status_code=403, detail="Cannot update orders of other restaurants")
    elif current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Only admin or manager can update order status")

    updated_order = await crud.update_order_status(db, db_order, status_update)
    logger.info(f"User {current_user.id} updated order {db_order.id} status to {updated_order.status}")
    return updated_order

@router.delete("/{order_id}")
async def delete_order(order_id: int, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    db_order = await crud.get_order_by_id(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    if current_user.role == "admin":
        pass
    elif current_user.role == "manager":
        if db_order.restaurant_id != current_user.restaurant_id:
            raise HTTPException(status_code=403, detail="Cannot delete orders of other restaurants")
    else:
        raise HTTPException(status_code=403, detail="Only admin or manager can delete orders")

    await crud.delete_order(db, db_order)
    logger.info(f"User {current_user.id} deleted order {db_order.id}")
    return {"detail": "Order deleted successfully"}
