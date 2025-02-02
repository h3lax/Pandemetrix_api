import argparse
# from .mariadb import fetch_data
from .postgresdb import insert_data
from .transform import transform_data
from .config import postgres_raw_config
import yaml

def load_queries():
    with open("queries.yaml", "r") as file:
        return yaml.safe_load(file)["queries"]

def get_query(query_name):
    queries = load_queries()
    return queries.get(query_name, None)

def main():
    parser = argparse.ArgumentParser(description="ETL CLI Tool")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--query', type=str, help='SQL query to execute')
    group.add_argument("--query-name", type=str, help="Name of predefined query")
    group.add_argument("--csv-file", type=str, help="Path to the input CSV file")
    parser.add_argument('--collection', type=str, required=True, help='MongoDB collection name')
    args = parser.parse_args()

    if args.csv_file:
        raw_data = args.csv_file
    else:
        if args.query_name:
            sql_query = get_query(args.query_name)
            if not sql_query:
                print(f"Query '{args.query_name}' not found! Check queries.yaml.")
                exit()
        else:
            sql_query = args.query

        # raw_data = fetch_data(mariadb_config, sql_query)
        if raw_data.empty:
            print("No data fetched from MariaDB.")
            return
    
    transformed_data = transform_data(raw_data)
    if transformed_data.empty:
        print("No data available after transformation.")
        return

    insert_data(postgres_raw_config, transformed_data, args.collection)