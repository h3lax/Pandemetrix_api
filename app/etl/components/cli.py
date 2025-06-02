import argparse
import io
import pandas as pd
import requests
import yaml
from config import Config
from .mongodb import insert_data
from .transform import transform_data

def load_queries():
    with open("app/etl/queries.yaml", "r") as file:
        return yaml.safe_load(file)

def get_query(query_name):
    queries = load_queries()["queries"]
    return queries.get(query_name, None)

def get_url(url_name):
    urls = load_queries()["urls"]
    return urls.get(url_name, None)

def download_csv(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content.decode('utf-8')

def main():
    parser = argparse.ArgumentParser(description="ETL CLI Tool")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--query', type=str, help='SQL query to execute')
    group.add_argument("--query-name", type=str, help="Name of predefined query")
    group.add_argument("--csv-file", type=str, help="Path to the input CSV file")
    group.add_argument("--download-url", type=str, help="URL to download the CSV file")
    group.add_argument("--download-url-name", type=str, help="Name of predefined URL to download the CSV file")
    parser.add_argument('--collection', type=str, required=True, help='postgres_raw table name')
    args = parser.parse_args()

    raw_data = None

    # Standardizing input as a DataFrame
    if args.csv_file:
        raw_data = pd.read_csv(args.csv_file)
    elif args.download_url:
        csv_content = download_csv(args.download_url)
        raw_data = pd.read_csv(io.StringIO(csv_content))
    elif args.download_url_name:
        url = get_url(args.download_url_name)
        if not url:
            print(f"URL '{args.download_url_name}' not found! Check queries.yaml.")
            exit()
        csv_content = download_csv(url)
        raw_data = pd.read_csv(io.StringIO(csv_content))
    else:
        if args.query_name:
            sql_query = get_query(args.query_name)
            if not sql_query:
                print(f"Query '{args.query_name}' not found! Check queries.yaml.")
                exit()
        else:
            sql_query = args.query

        # raw_data = fetch_data(mariadb_config, sql_query)

    if raw_data is None:
        print("No data source provided. Exiting.")
        return

    # Now transform_data() always gets a DataFrame
    transformed_data = transform_data(raw_data)
    
    if transformed_data.empty:
        print("No data available after transformation.")
        return
    
    # Show sample and column types before proceeding
    print("\n Sample of transformed data:")
    print(transformed_data.head(5))  # Show first 5 rows
    print("\n Column types:")
    print(transformed_data.dtypes)

    confirm = input("\nProceed with database insertion? (Y/N): ").strip().lower()
    if confirm != 'y':
        print("Insertion aborted.")
        return
    else:
        print("Inserting data into database...")

    insert_data(Config.MONGODB_CONFIG, transformed_data, args.collection)
