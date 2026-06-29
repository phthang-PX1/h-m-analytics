import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd

PROJECT_ID = "project-group4-id"
GOLD_DATASET = "Dataset1_Silver_Dataset1_Gold"
SILVER_DATASET = "Dataset1_Silver_Dataset1_Silver"
BRONZE_DATASET = "Dataset1_Bronze"


@st.cache_resource(show_spinner=False)
def get_client() -> bigquery.Client:
    """Return a cached BigQuery client using Streamlit secrets."""
    creds_dict = dict(st.secrets["gcp_service_account"])
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    return bigquery.Client(project=PROJECT_ID, credentials=credentials)


@st.cache_data(ttl=3600, show_spinner=False)
def run_query(sql: str) -> pd.DataFrame:
    """Execute a SQL query and return a DataFrame (cached 1 hour)."""
    client = get_client()
    job = client.query(sql)
    return job.result().to_dataframe()


def run_queries_parallel(sql_dict: dict) -> dict:
    """Run multiple queries in parallel. sql_dict = {key: sql_string}
    Returns {key: DataFrame}."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    client = get_client()

    def _run(key, sql):
        return key, client.query(sql).result().to_dataframe()

    results = {}
    with ThreadPoolExecutor(max_workers=min(len(sql_dict), 8)) as pool:
        futures = {pool.submit(_run, k, s): k for k, s in sql_dict.items()}
        for future in as_completed(futures):
            key, df = future.result()
            results[key] = df
    return results


def run_query_uncached(sql: str) -> pd.DataFrame:
    """Run a query without caching — used for ad-hoc GenBI queries."""
    client = get_client()
    return client.query(sql).result().to_dataframe()


def gold(table: str) -> str:
    return f"`{PROJECT_ID}.{GOLD_DATASET}.{table}`"


def silver(table: str) -> str:
    return f"`{PROJECT_ID}.{SILVER_DATASET}.{table}`"
