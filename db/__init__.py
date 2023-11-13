from .base import metadata, engine, DATABASE_URL

from .data_base import chats, message_routing




metadata.create_all(bind=engine)