"""DuckDB 마트 연결 및 SQL 실행."""
from pathlib import Path
import duckdb, pandas as pd

MART_PATH = Path(__file__).parent.parent / "data" / "mart.duckdb"
CSV_PATH  = Path(__file__).parent.parent / "data" / "fact_events.csv"

def get_connection() -> duckdb.DuckDBPyConnection:
    raise NotImplementedError

def build_mart(conn: duckdb.DuckDBPyConnection) -> None:
    raise NotImplementedError

def run_query(sql: str) -> pd.DataFrame:
    raise NotImplementedError

def _validate_select_only(sql: str) -> None:
    raise NotImplementedError
