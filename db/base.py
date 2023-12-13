from databases import Database
from sqlalchemy import create_engine, MetaData
import os




DATABASE_URL = "postgresql://root:root@bot_db:5432/bot_data" #os.getenv('DATABASE_URL')

#DATABASE_URL = "postgresql://root:root@extrabot.ru:32704/bot_data"

database = Database(DATABASE_URL)
metadata = MetaData()
engine = create_engine(
    DATABASE_URL,
)