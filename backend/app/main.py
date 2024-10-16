from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, status, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from app.utils.config import Config
from app.utils.turnstile import Turnstile
from beanie import Document, init_beanie, PydanticObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MongoDB client and database
client = AsyncIOMotorClient(Config().mongo_uri)
database = client[Config().database_name]

# Pydantic model for items
class Item(Document):
    content: str
    expiration: datetime
    max_views: int = 0
    views: int = 0
    created: datetime = Field(default_factory=datetime.utcnow)
    source: str

    class Settings:
        collection = "items"


# Initialize the Beanie ODM
async def init():
    await init_beanie(database, document_models=[Item])


@app.on_event("startup")
async def on_startup():
    await init()
    # Start cleanup tasks, such as purging old data hourly
    scheduler.add_job(purge_old_data, "interval", hours=1)
    scheduler.start()
    
scheduler = AsyncIOScheduler()


async def purge_old_data():
    """Clear out old and expired items that haven't been requested."""
    await Item.find_many(Item.expiration < datetime.utcnow()).delete()


@app.get("/v1/public/{item_id}/")
async def get_item(item_id: PydanticObjectId, turnstile_response: str = None):
    validation = True
    if not Config().turnstile_disabled:
        try:
            ts_client = Turnstile(Config().turnstile_sitekey, Config().turnstile_secret)
            validation = ts_client.validate_response(turnstile_response)
        except ValueError as e:
            if "secret" in e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        if not validation:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    item = await Item.get(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if item.expiration < datetime.now(timezone.utc):
        await item.delete()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if item.max_views != 0 and item.views >= item.max_views:
        await item.delete()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    item.views += 1
    await item.save()
    return item


class CreateItemRequest(BaseModel):
    content: str
    expiry_time: datetime
    max_views: int = 0


@app.post("/v1/public/")
async def create_item(request: CreateItemRequest, request_: Request, turnstile_response: str = None):
    validation = True
    if not Config().turnstile_disabled:
        try:
            ts_client = Turnstile(Config().turnstile_sitekey, Config().turnstile_secret)
            validation = ts_client.validate_response(turnstile_response)
        except ValueError as e:
            if "secret" in e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        if not validation:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    expiry_time = request.expiry_time.astimezone(timezone.utc)
    if expiry_time < datetime.now(timezone.utc):
        logger.error(f"Expiry time in the past, {expiry_time} < {datetime.now(timezone.utc)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expiry time in the past")

    if expiry_time > datetime.now(timezone.utc) + timedelta(days=30):
        logger.error(f"Expiry time too far in the future, {expiry_time} < {datetime.now(timezone.utc)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expiry time too far in the future")

    client_ip = request_.client.host
    if len(request.content) > 128:
        logger.error("Content too long")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content too long")

    item = Item(
        content=request.content,
        expiration=expiry_time,
        created=datetime.utcnow(),
        source=client_ip,
        views=0,
        max_views=request.max_views,
    )
    await item.insert()
    return {"id": str(item.id)}


@app.get("/publicv1/tea")
async def get_tea():
    return {status.HTTP_418_IM_A_TEAPOT: "I'm a teapot!"}
