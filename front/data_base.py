import psycopg2
import datetime
from dateutil.relativedelta import relativedelta
from collections import defaultdict
class InfoChat:
    def __init__(self,  name: str, id: int = 0,) -> None:
        self.id = id
        self.name = name


class Chat:
    def __init__(
        self,
        chat_name,
        keywords: list,
        recipient: list,
        is_anonym: bool, 
        not_duplicate: bool = False,
        excludewords:str = '',
        prefix: str = '',
        id: int = 0
    ) -> None:
        self.id = id
        self.chat_name = chat_name
        self.keywords = keywords
        self.excludewords = excludewords
        self.recipient = recipient 
        self.is_anonym = is_anonym
        self.not_duplicate = not_duplicate
        self.prefix =prefix


class InfoAllChat:
    def __init__(self, all_chat, recipient) -> None:
        self.all_chat = all_chat
        self.recipient= recipient
        self.data_dict = {}

def get_db_connection():
    conn = psycopg2.connect(
        host="extrabot.ru",
        port="32704",
        database="bot_data",
        user='root',
        password='root'
    )
    return conn



        


def get_tiggers():
    chats = []
    query = 'SELECT * FROM MESSAGE_ROUTING ORDER BY MESSAGE_ROUTING.id;'
    query_chats = 'SELECT * FROM CHATS ORDER BY CHATS.name;'
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query_chats)
            all_chat = cur.fetchall()
    chat_data = {dt[0]: dt[2] for dt in all_chat}

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            routing = cur.fetchall()
    for dt in routing:

        chats.append(
            Chat(
                chat_name=InfoChat(id=dt[1], name=chat_data[dt[1]]),
                keywords=dt[3],
                recipient=InfoChat(id=dt[2], name=chat_data[dt[2]]),
                excludewords=dt[4] if dt[4] is not None else '',
                is_anonym = dt[5] if dt[5] is not None else False,
                not_duplicate = dt[6] if dt[6] is not None else False,
                prefix=dt[7],
                id=dt[0]
            )
        )
    return chats


def get_tigger(chats: InfoAllChat, id) -> Chat:
    query = 'SELECT * FROM MESSAGE_ROUTING WHERE id = %s;'
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (str(id),))
            routing = cur.fetchone()
    print(routing)
    
    return Chat(
        chat_name=chats.data_dict[routing[1]],
        keywords=routing[3],
        recipient=chats.data_dict[routing[2]],
        excludewords=routing[4] if routing[4] is not None else '',
        is_anonym = routing[5] if routing[5] is not None else False,
        not_duplicate = routing[6] if routing[6] is not None else False,
        prefix=routing[7],
        id=routing[0]
    )


def update_tigger(
    addchat_id,
    sender_id: str,
    recipient_id: str,
    trigger_words: str,
    exclude_words: str,
    is_anonym: bool,
    not_duplicate: bool,
    prefix: str,
) -> None:
    print('update_tigger')
    print(recipient_id)
    if sender_id == recipient_id:
        return
    search_sender = """SELECT chats.id, chats.is_writable FROM chats INNER JOIN message_routing 
    ON chats.id = message_routing.sender_id WHERE chats.id = %s;"""
    chat_query = "SELECT chats.id, chats.is_writable FROM chats WHERE chats.id = %s;"

    query = "UPDATE MESSAGE_ROUTING SET sender_id = %s, recipient_id = %s, trigger_words = %s, exclude_words =%s, is_anonym=%s, not_duplicate=%s, prefix=%s WHERE id = %s;"
    data = (sender_id, recipient_id, trigger_words, exclude_words, is_anonym, not_duplicate, prefix, addchat_id)
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(search_sender, (recipient_id,))
            sender_chat = cur.fetchall()
            cur.execute(chat_query, (recipient_id,))
            chat_data = cur.fetchone()
            if sender_chat ==[] and chat_data[1]:
                cur.execute(query, data)
        conn.commit()


def delete_tigger(addchat_id) -> None:
    print('delete_tigger')
    query = "DELETE FROM MESSAGE_ROUTING WHERE id = %s;"
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (addchat_id,))
        conn.commit()

def get_all_chat() -> InfoAllChat:
    result = InfoAllChat([], [])
    query_chats = 'SELECT * FROM CHATS ORDER BY CHATS.name;'
    query_routquery_routee = 'SELECT DISTINCT message_routing.sender_id, message_routing.recipient_id FROM message_routing;'
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query_chats)
            all_chat = cur.fetchall()
            cur.execute(query_routquery_routee)
            routing_chat = cur.fetchall()
    recipient = [r[1] for r in routing_chat]
    sender = [r[0] for r in routing_chat]
    for ch in all_chat:
        result.data_dict[ch[0]]=(InfoChat(id=ch[0], name=ch[2]))
        if ch[0] not in recipient:
            result.all_chat.append(InfoChat(id=ch[0], name=ch[2]))
        if ch[3] and ch[0] not in sender:
            result.recipient.append(InfoChat(id=ch[0], name=ch[2]))
    return result 



def add_tiggers(
    sender_id: str,
    recipient_id: str,
    trigger_words: str,
    exclude_words: str,
    is_anonym: bool,
    not_duplicate: bool,
    prefix: str
) -> None:
    print('sender_id', sender_id, 'recipient_id', recipient_id, 'trigger_words', trigger_words)
    if sender_id == recipient_id:
        return
    search_sender = """SELECT chats.id, chats.is_writable FROM chats INNER JOIN message_routing 
    ON chats.id = message_routing.sender_id WHERE chats.id = %s;"""
    chat_query = "SELECT chats.id, chats.is_writable FROM chats WHERE chats.id = %s;"
    query = "INSERT INTO MESSAGE_ROUTING (sender_id, recipient_id, trigger_words, exclude_words, is_anonym, not_duplicate, prefix) VALUES (%s, %s, %s, %s, %s, %s, %s);"
    data = (sender_id, recipient_id, trigger_words, exclude_words, is_anonym, not_duplicate, prefix)
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(search_sender, (recipient_id,))
            sender_chat = cur.fetchall()
            cur.execute(chat_query, (recipient_id,))
            chat_data = cur.fetchone()
            if sender_chat ==[] and chat_data[1]:
                cur.execute(query, data)      
        conn.commit()

  
'''message_routing = Table(
    'message_routing',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True, unique= True),
    Column('sender_id', Integer, ForeignKey('chats.id', ondelete="CASCADE"), nullable=False),
    Column('recipient_id', Integer, ForeignKey('chats.id', ondelete="CASCADE"), nullable=False),
    Column('trigger_words', String)


def update_chat(chat_id: int, tg_chat_id: str, name: str, is_writable: bool) -> None:
    query = "UPDATE CHATS SET tg_chat_id = %s, name = %s, is_writable = %s WHERE id = %s;"
    data = (tg_chat_id, name, is_writable, chat_id)
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, data)
        conn.commit()


)'''