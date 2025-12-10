import pytest
from httpx import AsyncClient
from main import app  # <-- importi i saktë për projektin tënd

@pytest.mark.asyncio
async def test_create_dish():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/dish/",
            json={
                "name": "Pizza",
                "description": "Cheese pizza",
                "price": 7.5,
                "menu_id": 1
            }
        )
    assert response.status_code == 200
    assert response.json()["name"] == "Pizza"

@pytest.mark.asyncio
async def test_get_dishes():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/dish/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
