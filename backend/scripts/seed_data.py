"""載入真實 CSV 到 market.duckdb"""
import json
import sys
from pathlib import Path
import pandas as pd

# 讓 scripts/ 能 import app/
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.db import get_conn, init_schema

DATA_DIR = Path(__file__).parent.parent / "data"


def load_monthly_wide(path: Path, value_col: str) -> pd.DataFrame:
    """載入 wide 月頻 CSV，melt 成 long，日期轉月底。"""
    df = pd.read_csv(path)
    df = df.rename(columns={df.columns[0]: "date"})
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m") + pd.offsets.MonthEnd(0)
    long_df = df.melt(id_vars="date", var_name="stock_id", value_name=value_col)
    long_df["stock_id"] = long_df["stock_id"].astype(str)
    long_df["date"] = long_df["date"].dt.date  # 轉 date 物件給 DuckDB
    return long_df


def load_daily_wide(path: Path, value_col: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.rename(columns={df.columns[0]: "date"})
    df["date"] = pd.to_datetime(df["date"]).dt.date
    long_df = df.melt(id_vars="date", var_name="stock_id", value_name=value_col)
    long_df["stock_id"] = long_df["stock_id"].astype(str)
    return long_df


def main():
    print("初始化 schema...")
    conn = get_conn()
    init_schema(conn)

    # === 月頻：4 個檔案 outer join ===
    print("載入月頻資料...")
    eps_df = load_monthly_wide(DATA_DIR / "eps.csv", "eps")
    rg_df  = load_monthly_wide(DATA_DIR / "earn_yoy.csv", "revenue_growth")
    pe_df  = load_monthly_wide(DATA_DIR / "pe_ratio.csv", "pe")
    pb_df  = load_monthly_wide(DATA_DIR / "pb_ratio.csv", "pb")

    monthly = (eps_df
        .merge(rg_df, on=["date", "stock_id"], how="outer")
        .merge(pe_df, on=["date", "stock_id"], how="outer")
        .merge(pb_df, on=["date", "stock_id"], how="outer"))

    # 四個指標都是 NaN 的列就是純粹沒資料，直接 drop
    monthly = monthly.dropna(subset=["eps", "revenue_growth", "pe", "pb"], how="all")
    print(f"  月頻資料: {len(monthly):,} 筆")

    conn.register("monthly_df", monthly)
    conn.execute("INSERT INTO monthly_data SELECT date, stock_id, eps, revenue_growth, pe, pb FROM monthly_df")
    conn.unregister("monthly_df")

    # === 日頻收盤價 ===
    print("載入收盤價...")
    price_df = load_daily_wide(DATA_DIR / "price.csv", "close")
    price_df = price_df.dropna(subset=["close"])
    print(f"  收盤價: {len(price_df):,} 筆")
    conn.register("price_df", price_df)
    conn.execute("INSERT INTO daily_price SELECT date, stock_id, close FROM price_df")
    conn.unregister("price_df")

    # === VIX ===
    print("載入 VIX...")
    vix = pd.read_csv(DATA_DIR / "vix_index.csv")
    vix.columns = ["date", "vix"]
    vix["date"] = pd.to_datetime(vix["date"]).dt.date
    vix = vix.dropna()
    print(f"  VIX: {len(vix):,} 筆")
    conn.register("vix_df", vix)
    conn.execute("INSERT INTO daily_macro SELECT date, vix FROM vix_df")
    conn.unregister("vix_df")

    # === 股票清單（從所有資料檔取聯集，從 JSON 取中文名）===
    print("載入股票清單...")
    with open(DATA_DIR / "stock_names.json", encoding="utf-8") as f:
        name_map = json.load(f)

    all_ids = set()
    for df in [eps_df, rg_df, pe_df, pb_df, price_df]:
        all_ids.update(df["stock_id"].unique())

    stocks = pd.DataFrame({
        "stock_id": sorted(all_ids),
    })
    stocks["stock_name"] = stocks["stock_id"].map(lambda x: name_map.get(x, x))
    stocks["sector"] = "Unknown"
    print(f"  股票: {len(stocks):,} 檔")
    conn.register("stocks_df", stocks)
    conn.execute("INSERT INTO stocks SELECT stock_id, stock_name, sector FROM stocks_df")
    conn.unregister("stocks_df")

    # === 驗證 ===
    print("\n=== 驗證 ===")
    for tbl in ["stocks", "monthly_data", "daily_price", "daily_macro"]:
        cnt = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        print(f"  {tbl}: {cnt:,} 筆")

    print("\n=== stocks 前 5 筆 ===")
    print(conn.execute("SELECT * FROM stocks ORDER BY stock_id LIMIT 5").fetchdf())

    print("\n=== 台積電 (2330) 最近 3 筆月頻資料 ===")
    print(conn.execute("""
        SELECT * FROM monthly_data
        WHERE stock_id = '2330'
        ORDER BY date DESC LIMIT 3
    """).fetchdf())

    print("\n=== 台積電 (2330) 最近 5 筆收盤價 ===")
    print(conn.execute("""
        SELECT * FROM daily_price
        WHERE stock_id = '2330'
        ORDER BY date DESC LIMIT 5
    """).fetchdf())

    print("\n=== VIX 最近 3 筆 ===")
    print(conn.execute("SELECT * FROM daily_macro ORDER BY date DESC LIMIT 3").fetchdf())

    conn.close()
    print("\n完成。")


if __name__ == "__main__":
    main()
