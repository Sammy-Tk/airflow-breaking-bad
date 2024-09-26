from airflow import DAG
from airflow.operators.python import PythonOperator
from google.cloud import bigquery
from datetime import datetime
import os

# Read GCP configuration from environment variables
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = os.getenv("BIGQUERY_DATASET_ID")
TABLE_ID = os.getenv("BIGQUERY_TABLE_ID")

# Create a simple table in BigQuery
def create_and_load_table():
    client = bigquery.Client()

    # Define the schema for the table
    schema = [
        bigquery.SchemaField("column1", "STRING"),
        bigquery.SchemaField("column2", "STRING")
    ]

    # Define the table and dataset
    table_ref = client.dataset(DATASET_ID).table(TABLE_ID)

    # Create the table if it doesn't exist
    try:
        table = client.get_table(table_ref)  # Attempt to get the table
        print(f"Table {TABLE_ID} already exists.")
    except Exception as e:
        table = bigquery.Table(table_ref, schema=schema)  # Create a new table
        table = client.create_table(table)
        print(f"Table {TABLE_ID} created.")

    # Insert sample data into the table
    rows_to_insert = [
        {"column1": "A", "column2": "B"},
        {"column1": "C", "column2": "D"},
        {"column1": "E", "column2": "F"},
        {"column1": "G", "column2": "H"},
        {"column1": "I", "column2": "J"}
    ]

    errors = client.insert_rows_json(table_ref, rows_to_insert)
    if errors == []:
        print(f"New rows added to {TABLE_ID}.")
    else:
        print(f"Errors while inserting rows: {errors}")

# Define the DAG
with DAG(
    dag_id="bigquery_alphabet_dag",
    start_date=datetime(2023, 9, 24),
    schedule_interval=None,
    catchup=False
) as dag:

    # Task to create the table and load data into BigQuery
    load_data_task = PythonOperator(
        task_id="load_data_to_bigquery",
        python_callable=create_and_load_table
    )

    load_data_task
