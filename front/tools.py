import psycopg2
import datetime
from dateutil.relativedelta import relativedelta
from collections import defaultdict

from .data_base import get_db_connection




class States:
    def __init__(self, scale) -> None:
        get_stat(scale)
        
        pass

def get_stat(scale):
    date_end = datetime.datetime.utcnow()
    if scale == 'month':
        date_start = date_end - relativedelta(months=7)
    elif scale == 'week':
        date_start = date_end - relativedelta(days=98)
    else:
        date_start = date_end - relativedelta(days=7)
    query = 'SELECT * FROM message_send_stats WHERE created_at BETWEEN : %s AND : %s'
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (date_start, date_end))
            data = cur.fetchall()

def parce_for_data(scale, data):
    result = defaultdict(int)
    if scale == 'month':
        for dt in data:
            key = str(dt.created_at).split(' ')[0].split('-')[1]
            result[key] += 1
        return result
    if scale == 'week':
        for dt in data:
            key = dt.created_at.isocalendar()[1]
            result[key] += 1
        return result
    
    for dt in data:
        key = str(dt.created_at).split(' ')[0].split('-')[2]
        result[key] += 1
    return result
    