from datetime import datetime, timedelta
from fastapi import FastAPI, status, Request
from .utils.config import Config
from .utils.db import DatabaseManager
from .utils.turnstile import Turnstile

app = FastAPI()

# Initialize the database manager
db = DatabaseManager(dbname=Config().dbname, user=Config().dbuser, password=Config().dbpassword, host=Config().dbhost)


@app.on_event("startup")
async def startup_event():
    # Create 'users' table if it does not exist
    db.create_table('items', {'id': 'TEXT PRIMARY KEY',
                              'content': 'TEXT',
                              'expiration': 'TIMESTAMP',
                              'created': 'TIMESTAMP',
                              'source': 'INET',
                              }
                    )


@app.get("/publicv1/{item_id}/")
async def get_item(item_id: int, turnstyle_response: str = None):
    
    validation = True
    if not Config().turnstyle_disabled:
        try:
            ts_client = Turnstile(Config().turnstyle_sitekey, Config().turnstyle_secret)
            validation = ts_client.validate_response(turnstyle_response)
        except ValueError as e:
            if "secret" in e:
                return status.HTTP_500_INTERNAL_SERVER_ERROR
            return status.HTTP_400_BAD_REQUEST, e
        if not validation:
            return status.HTTP_403_FORBIDDE
        
        item = db.items.get_pydantic_first(f'id = {item_id}')
        
        # Check if the item is expired
        if item.expiration and item.expiration < datetime.now():
            item.delete()
            return status.HTTP_404_NOT_FOUND
        
        return item.json()

    if not validation:
        return status.HTTP_403_FORBIDDEN


@app.post("/publicv1/")
async def create_item(content: str, expiry_time: datetime, request: Request, turnstyle_response: str = None):
    
    validation = True
    if not Config().turnstyle_disabled:
        try:
            ts_client = Turnstile(Config().turnstyle_sitekey, Config().turnstyle_secret)
            validation = ts_client.validate_response(turnstyle_response)
        except ValueError as e:
            if "secret" in e:
                return status.HTTP_500_INTERNAL_SERVER_ERROR
            return status.HTTP_400_BAD_REQUEST, e
        if not validation:
            return status.HTTP_403_FORBIDDE
        
    
    client_ip = request.client.host
    if len(content) > 128:
        return status.HTTP_400_BAD_REQUEST, "Content too long"
    try:
        db.items.insert({
                            'content': content,
                            'expiration': expiry_time,
                            'created': datetime.now(),
                            'source': client_ip,
                        }, id_length=8)
    except Exception as e:
        print(e)
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return 


@app.get("/publicv1/tea")
async def get_tea():
    return {status.HTTP_418_IM_A_TEAPOT: "I'm a teapot!"}
