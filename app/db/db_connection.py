import logging
import psycopg2
from psycopg2 import pool
import pandas as pd
import json
from app.agents.utils import db_data_to_df
from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USERNAME

username = DB_USERNAME
password = DB_PASSWORD
host = DB_HOST
port = DB_PORT
dbname = DB_NAME

logger = logging.getLogger(__name__)


def create_connection_pool():
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1,
            10,
            user=username,
            password=password,
            host=host,
            port=port,
            database=dbname,
        )
        if connection_pool:
            print("Connection pool created successfully")
        return connection_pool
    except Exception as e:
        print(f"Error creating connection pool: {e}")
        return None


def execute_query(query, params=None):
    connection_pool = create_connection_pool()
    if connection_pool:
        conn = connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()
                return result
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return None
        finally:
            connection_pool.putconn(conn)


def insert_or_update_company_data(company_name, data):
    connection_pool = create_connection_pool()
    if not connection_pool:
        logger.error("Connection pool not available.")
        return

    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cursor:
            query = """
            INSERT INTO company_data (company_name, data)
            VALUES (%s, %s)
            ON CONFLICT (company_name)
            DO UPDATE SET data = EXCLUDED.data;
            """
            cursor.execute(query, (company_name, json.dumps(data)))
            conn.commit()
            logger.info(
                f"Data for company '{company_name}' inserted/updated successfully."
            )
    except Exception as e:
        logger.error(f"Error inserting/updating data: {e}")
    finally:
        connection_pool.putconn(conn)


def create_table():
    query = """
        CREATE TABLE company_data (
        company_id SERIAL PRIMARY KEY,
        company_name VARCHAR(255) NOT NULL,
        data JSONB,
        UNIQUE (company_name)
        );
    """
    try:
        connection_pool = create_connection_pool()
        if connection_pool:
            conn = connection_pool.getconn()
            try:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    conn.commit()  # Commit the transaction
                    print("Table created successfully.")
            except Exception as e:
                logger.error(f"Error creating table: {e}")
            finally:
                connection_pool.putconn(conn)
        else:
            logger.error("Connection pool not available.")
    except Exception as e:
        logger.error(f"Error inserting data: {e}")


def fetch_company_data(company_name):
    connection_pool = create_connection_pool()
    if not connection_pool:
        logger.error("Connection pool not available.")
        return None

    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cursor:
            query = """
            SELECT data
            FROM company_data
            WHERE company_name = %s;
            """
            cursor.execute(query, (company_name,))
            result = cursor.fetchone()
            if result:
                logger.info(f"Data for company '{company_name}' fetched successfully.")
                return json.loads(result[0])
            else:
                logger.warning(f"No data found for company '{company_name}'.")
                return None
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return None
    finally:
        connection_pool.putconn(conn)


data = fetch_company_data("Apple")
a, b, c = db_data_to_df(data)
print(c)
