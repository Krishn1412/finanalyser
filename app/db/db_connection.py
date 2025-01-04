import logging
import psycopg2
from psycopg2 import pool
import pandas as pd
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
            1, 10, user=username, password=password, host=host, port=port, database=dbname
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

def insert_dataframe_to_db(df, table_name):
    connection_pool = create_connection_pool()
    if connection_pool:
        conn = connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                columns = df.columns.tolist()
                values_placeholder = ", ".join(["%s"] * len(columns))
                insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({values_placeholder})"

                for row in df.itertuples(index=False, name=None):
                    cursor.execute(insert_query, row)
                conn.commit()
                print(f"Data inserted successfully into {table_name}!")
        except Exception as e:
            logger.error(f"Error inserting data: {e}")
            conn.rollback()
        finally:
            connection_pool.putconn(conn)

# query = "SELECT * FROM your_table_name LIMIT 5;"
# data = execute_query(query)
# # if data:
# #     print("Data from PostgreSQL:")
# #     for row in data:
# #         print(row)

# data_frame = pd.DataFrame({
#     'company_name': ['Apple', 'Microsoft', 'Google'],
#     'revenue': [100000, 120000, 130000],
#     'profit': [20000, 30000, 40000]
# })

# # Insert the data into the PostgreSQL table
# insert_dataframe_to_db(data_frame, 'company_financials')
# print("start table")
# print(create_table())

query = "SELECT * FROM company_data LIMIT 5;"
data = execute_query(query)
print(data)