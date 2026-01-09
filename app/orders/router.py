from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from . import crud, schemas
from app.auth.oauth2 import require_role, get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=schemas.OrderRead)
async def create_order(
    order: schemas.OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await crud.create_order(db, order, current_user.id)

@router.get("/my-orders", response_model=List[schemas.OrderRead])
async def get_my_orders(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await crud.get_orders_by_user(db, current_user.id)

@router.get(
    "/",
    response_model=List[schemas.OrderRead],
    dependencies=[Depends(require_role("admin"))]
)
async def get_all_orders(db: AsyncSession = Depends(get_db)):
    return await crud.get_all_orders(db)

@router.patch(
    "/{order_id}/status",
    response_model=schemas.OrderRead,
    dependencies=[Depends(require_role("admin"))]
)
async def update_order_status(
    order_id: int,
    status_update: schemas.OrderUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_order = await crud.get_order_by_id(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return await crud.update_order_status(db, db_order, status_update)

@router.delete(
    "/{order_id}",
    dependencies=[Depends(require_role("admin"))]
)
async def delete_order(order_id: int, db: AsyncSession = Depends(get_db)):
    db_order = await crud.get_order_by_id(db, order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    await crud.delete_order(db, db_order)
    return {"detail": "Order deleted successfully"}

