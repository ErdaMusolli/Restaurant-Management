import pytest
from httpx import AsyncClient
from main import app  # <-- importi i saktë për projektin tënd

@pytest.mark.asyncio
async def test_create_menu():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/menu/", json={"name": "Breakfast", "description": "Morning menu"})
    assert response.status_code == 200
    assert response.json()["name"] == "Breakfast"

@pytest.mark.asyncio
async def test_get_menus():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/menu/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

