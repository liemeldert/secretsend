from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, status, Request
from .utils.config import Config
from .utils.db import DatabaseManager
from .utils.turnstile import Turnstile
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

app = FastAPI()

# Initialize the database manager
db = DatabaseManager(dbname=Config().dbname, user=Config().dbuser, password=Config().dbpassword, host=Config().dbhost)

scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup_event():
    # Create 'users' table if it does not exist
    db.create_table('items', {'id': 'TEXT PRIMARY KEY',
                              'content': 'TEXT',
                              'expiration': 'TIMESTAMP',
                              'max_views': 'INTEGER',
                              'views': 'INTEGER',
                              'created': 'TIMESTAMP',
                              'source': 'INET',
                              }
                    )
    # Start cleanup tasks
    scheduler.add_job(purge_old_data, "interval", hours=1)
    scheduler.start()


def purge_old_data():
    db.items.delete_many({"expiration": {"$lt": datetime.now()}})


@app.get("/publicv1/{item_id}/")
async def get_item(item_id: str, turnstile_response: str = None):
    validation = True
    if not Config().turnstile_disabled:
        try:
            ts_client = Turnstile(Config().turnstile_sitekey, Config().turnstile_secret)
            validation = ts_client.validate_response(turnstile_response)
        except ValueError as e:
            if "secret" in e:
                return status.HTTP_500_INTERNAL_SERVER_ERROR
            return status.HTTP_400_BAD_REQUEST, e
        if not validation:
            return status.HTTP_403_FORBIDDEN
    if not validation:
        return status.HTTP_403_FORBIDDEN
        
    item_pd = db.items.get_first_pydantic(f'id = {item_id}')
    item = db.items.get_first(f'id = {item_id}')
    
    localised_expiration = pytz.utc.localize(expiry_time)
    
    # Check if the item is expired
    if localised_expiration and localised_expiration < datetime.now(timezone.utc):
        item_pd.delete()
        return status.HTTP_404_NOT_FOUND
    
    if item_pd.max_views != 0 and item_pd.views >= item_pd.max_views:
        item_pd.delete()
        return status.HTTP_404_NOT_FOUND
    # wow that's bad syntax
    item.update("views", item_pd.views + 1)
    print(item_pd)
    return item_pd.json()



@app.post("/publicv1/")
async def create_item(content: str, expiry_time: datetime, request: Request, max_views:int = 0, turnstile_response: str = None):
    """Creates an encrypted password item
    expiry_time may not be more than 30 days in the future.

    Args:
        content (str): pre-encrppted content
        expiry_time (datetime): datetime of when the item should expire in iso 8601 format (ex. 2048-09-15T15:53:00+05:00)
        request (Request): FastAPI request object
        turnstile_response (str, optional): turnstile verification token, only needed when enabled in env. Defaults to None.

    Returns:
        _type_: _description_
    """
    validation = True
    if not Config().turnstile_disabled:
        try:
            ts_client = Turnstile(Config().turnstile_sitekey, Config().turnstile_secret)
            validation = ts_client.validate_response(turnstile_response)
        except ValueError as e:
            if "secret" in e:
                return status.HTTP_500_INTERNAL_SERVER_ERROR
            return status.HTTP_400_BAD_REQUEST, e
        if not validation:
            return status.HTTP_403_FORBIDDE
    
    expiry_time = expiry_time.astimezone(timezone.utc) # Convert to UTC
    # Check if the item is expired already
    if expiry_time < datetime.now(timezone.utc):
        return status.HTTP_400_BAD_REQUEST, "Expiry time in the past"
    
    # Check if the item will expire after 30 days, the maximum allowed
    if expiry_time > datetime.now(timezone.utc) + timedelta(days=30):
        return status.HTTP_400_BAD_REQUEST, "Expiry time too far in the future"

    client_ip = request.client.host
    if len(content) > 128:
        return status.HTTP_400_BAD_REQUEST, "Content too long"
    try:
        new_item_id = db.items.insert({
            'content': content,
            'expiration': expiry_time,
            'created': datetime.now(),
            'source': client_ip,
            'views': 0,
            'max_views': max_views,
        }, id_length=8)
    except Exception as e:
        print(e)
        return status.HTTP_500_INTERNAL_SERVER_ERROR

    return {"id": new_item_id}



@app.get("/publicv1/tea")
async def get_tea():
    return {status.HTTP_418_IM_A_TEAPOT: "I'm a teapot!"}
