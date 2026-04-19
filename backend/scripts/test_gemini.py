"""測試 Gemini 解析中文查詢。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.gemini import parse_query


QUERIES = [
    "幫我回測低 PE 前 20% 的投資策略",
    "我想看現在 EPS 成長率最高的前 30 檔股票",
    "便宜股票的歷史表現如何？",
    "最近營收動能最強的是哪些",
    "從 2020 年開始，高 EPS 的策略年化報酬多少",
    "PB 最低的前 10% 股票現在是哪些",
]


def main():
    for q in QUERIES:
        print(f"\n{'='*60}")
        print(f"Q: {q}")
        try:
            result = parse_query(q)
            p = result.params
            print(f"explanation: {result.explanation}")
            print(f"  mode={p.mode}, factor={p.factor}, direction={p.direction}, percentile={p.percentile}")
            print(f"  feature={p.feature.type}(window={p.feature.window})")
            print(f"  {p.start_date} ~ {p.end_date}")
        except Exception as e:
            print(f"  ERROR: {e}")


if __name__ == "__main__":
    main()
