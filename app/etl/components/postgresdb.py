from psycopg2 import connect, sql

def get_connection(config):
    return connect(
        host=config['host'],
        port=config.get('port', 5432),
        user=config.get('username'),
        password=config.get('password'),
        dbname=config['database']
    )

def create_table(conn, table_name, columns):
    try:
        cursor = conn.cursor()
        
        # Generate the SQL query for creating the table
        columns_with_types = ', '.join([f"{col} TEXT" for col in columns])
        query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
            sql.Identifier(table_name),
            sql.SQL(columns_with_types)
        )
        
        cursor.execute(query)
        conn.commit()
        cursor.close()
        print(f"Table '{table_name}' created successfully.")
    except Exception as e:
        print(f"Error creating table in PostgreSQL: {e}")
        raise

def insert_data(config, data, table_name):
    try:
        conn = get_connection(config)
        
        # Create table before inserting data
        create_table(conn, table_name, data.columns)
        
        cursor = conn.cursor()
        
        # Generate the SQL query for inserting data
        columns = data.columns
        query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table_name),
            sql.SQL(', ').join(map(sql.Identifier, columns)),
            sql.SQL(', ').join(sql.Placeholder() * len(columns))
        )
        
        # Execute the query for each row of data
        for row in data.itertuples(index=False, name=None):
            cursor.execute(query, row)
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Data inserted into table '{table_name}' successfully.")
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        raise

# etl/transform.py
def transform_data(data):
    print("Data transformation complete.")
    return data