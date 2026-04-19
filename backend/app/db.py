import duckdb
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "market.duckdb"

def get_conn():
    return duckdb.connect(str(DB_PATH))

def init_schema(conn=None):
    """建立（或重建）四張表。會先 DROP 再建。"""
    close_after = False
    if conn is None:
        conn = get_conn()
        close_after = True

    conn.execute("DROP TABLE IF EXISTS monthly_data")
    conn.execute("DROP TABLE IF EXISTS daily_price")
    conn.execute("DROP TABLE IF EXISTS daily_macro")
    conn.execute("DROP TABLE IF EXISTS stocks")

    conn.execute("""
        CREATE TABLE stocks (
            stock_id VARCHAR PRIMARY KEY,
            stock_name VARCHAR,
            sector VARCHAR
        )
    """)
    conn.execute("""
        CREATE TABLE monthly_data (
            date DATE,
            stock_id VARCHAR,
            eps DOUBLE,
            revenue_growth DOUBLE,
            pe DOUBLE,
            pb DOUBLE,
            PRIMARY KEY(date, stock_id)
        )
    """)
    conn.execute("""
        CREATE TABLE daily_price (
            date DATE,
            stock_id VARCHAR,
            close DOUBLE,
            PRIMARY KEY(date, stock_id)
        )
    """)
    conn.execute("""
        CREATE TABLE daily_macro (
            date DATE PRIMARY KEY,
            vix DOUBLE
        )
    """)
    if close_after:
        conn.close()
