import pytest
import asyncio
from httpx import AsyncClient
from datetime import datetime, timedelta
from fastapi import status
from main import app, init, Item  # Assuming your FastAPI app is in main.py

# Initialize the database for testing
@pytest.fixture(scope="module")
async def initialize_db():
    await init()
    yield
    await Item.delete_all()

@pytest.fixture
async def client(initialize_db):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def item_data():
    expiry_time = datetime.now() + timedelta(days=1)
    return {
        "content": "Test content",
        "expiry_time": expiry_time.isoformat(),
        "max_views": 5
    }

@pytest.mark.asyncio
async def test_create_item(client, item_data):
    response = await client.post("/publicv1/", json=item_data)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert "id" in response_data

@pytest.mark.asyncio
async def test_create_item_expiry_time_in_past(client, item_data):
    item_data["expiry_time"] = (datetime.now() - timedelta(days=1)).isoformat()
    response = await client.post("/publicv1/", json=item_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_create_item_expiry_time_too_far_in_future(client, item_data):
    item_data["expiry_time"] = (datetime.now() + timedelta(days=31)).isoformat()
    response = await client.post("/publicv1/", json=item_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_get_item(client, item_data):
    # Create an item first
    create_response = await client.post("/publicv1/", json=item_data)
    assert create_response.status_code == status.HTTP_200_OK
    item_id = create_response.json()["id"]

    # Fetch the item
    get_response = await client.get(f"/publicv1/{item_id}/")
    assert get_response.status_code == status.HTTP_200_OK
    response_data = get_response.json()
    assert response_data["content"] == item_data["content"]

@pytest.mark.asyncio
async def test_get_item_not_found(client):
    response = await client.get("/publicv1/nonexistent_id/")
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_get_item_expired(client, item_data):
    item_data["expiry_time"] = (datetime.now() - timedelta(days=1)).isoformat()
    create_response = await client.post("/publicv1/", json=item_data)
    assert create_response.status_code == status.HTTP_200_OK
    item_id = create_response.json()["id"]

    get_response = await client.get(f"/publicv1/{item_id}/")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_get_item_exceed_max_views(client, item_data):
    item_data["max_views"] = 1
    create_response = await client.post("/publicv1/", json=item_data)
    assert create_response.status_code == status.HTTP_200_OK
    item_id = create_response.json()["id"]

    # First view should succeed
    first_view_response = await client.get(f"/publicv1/{item_id}/")
    assert first_view_response.status_code == status.HTTP_200_OK

    # Second view should result in a 404 as max_views is 1
    second_view_response = await client.get(f"/publicv1/{item_id}/")
    assert second_view_response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_get_tea(client):
    response = await client.get("/publicv1/tea")
    assert response.status_code == status.HTTP_418_IM_A_TEAPOT
