import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import urllib.parse as urlparse
from app.utils.logger import get_logger
logger = get_logger(__name__)

def create_db_if_not_exists(db_url: str):
    parsed_url = urlparse.urlparse(db_url)
    dbname = parsed_url.path[1:] 
    user = parsed_url.username
    password = parsed_url.password
    host = parsed_url.hostname
    port = parsed_url.port

    conn = psycopg2.connect(
        dbname='postgres',
        user=user,
        password=password,
        host=host,
        port=port
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (dbname,))
    exists = cur.fetchone()

    if not exists:
        logger.info(f"Database '{dbname}' does not exist. Creating...")
        cur.execute(f'CREATE DATABASE "{dbname}"')
        logger.info(f"Database '{dbname}' created successfully.")
    else:
        logger.info(f"Database '{dbname}' already exists.")

    cur.close()
    conn.close()