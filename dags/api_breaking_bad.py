from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from google.cloud import bigquery
from google.api_core.exceptions import NotFound  # Correctly import NotFound
from datetime import datetime
import requests
import os

# Read GCP configuration from environment variables
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = os.getenv("BIGQUERY_DATASET_ID")
TABLE_ID = "breaking_bad"  # The new table name

def fetch_and_store_quotes():
    client = bigquery.Client()
    dataset_ref = client.dataset(DATASET_ID)
    table_ref = dataset_ref.table(TABLE_ID)

    # Check if the table exists
    try:
        client.get_table(table_ref)  # Check if the table exists
        print(f"Table {TABLE_ID} already exists.")
    except NotFound:
        # If the table does not exist, create it
        schema = [
            bigquery.SchemaField("quote", "STRING"),
            bigquery.SchemaField("author", "STRING"),
        ]
        table = bigquery.Table(table_ref, schema=schema)
        client.create_table(table)
        print(f"Table {TABLE_ID} created.")

    # Fetch quotes from the API
    response = requests.get("https://api.breakingbadquotes.xyz/v1/quotes")
    quotes = response.json()

    # Prepare the data to insert into BigQuery
    rows_to_insert = [{"quote": item['quote'], "author": item['author']} for item in quotes]

    # Insert quotes into the BigQuery table
    errors = client.insert_rows_json(table_ref, rows_to_insert)
    if errors:
        print(f"Errors while inserting rows: {errors}")
    else:
        print(f"Inserted quotes into {TABLE_ID}.")

# Define the DAG
with DAG(
    dag_id="fetch_breaking_bad_quotes_dag",
    start_date=datetime(2023, 9, 24),
    schedule_interval=None,
    catchup=False
) as dag:
    
    # Task to fetch quotes and store them in BigQuery
    fetch_and_store_task = PythonOperator(
        task_id="fetch_and_store_quotes",
        python_callable=fetch_and_store_quotes
    )

    fetch_and_store_task
