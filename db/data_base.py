import datetime
from sqlalchemy import Table, Column, String, Boolean, Integer, DateTime, ForeignKey

from .base import metadata


chats = Table(
    'chats',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True, unique= True),
    Column('tg_chat_id', String),
    Column('name', String),
    Column('is_writable', Boolean),
)

message_routing = Table(
    'message_routing',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True, unique= True),
    Column('sender_id', Integer, ForeignKey('chats.id', ondelete="CASCADE"), nullable=False),
    Column('recipient_id', Integer, ForeignKey('chats.id', ondelete="CASCADE"), nullable=False),
    Column('trigger_words', String)
)
