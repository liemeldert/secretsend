import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        
        # Postgres config
        # self.dbname = os.environ.get('DB_NAME')
        # self.dbuser = os.environ.get('DB_USER')
        # self.dbpassword = os.environ.get('DB_PASSWORD')
        # self.dbhost = os.environ.get('DB_HOST')
        
        # Mongo config
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://root:example@localhost:27017")
        self.database_name = os.getenv("DATABASE_NAME", "secretsend")
        
        # Turnstyle config
        self.turnstile_sitekey = os.environ.get('TURNSTYLE_SITEKEY')
        self.turnstile_secret = os.environ.get('TURNSTYLE_SECRET')
        self.turnstile_disabled = bool(os.environ.get('TURNSTYLE_DISABLED', False))
        
        # print("db_host = " + str(self.dbhost))
