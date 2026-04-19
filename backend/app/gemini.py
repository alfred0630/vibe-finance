"""Gemini NL → ParsedParams 解析器"""
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from .schemas import ParsedParams, ParseResponse

# 載入 .env
load_dotenv(Path(__file__).parent.parent / ".env")

_API_KEY = os.getenv("GEMINI_API_KEY")
if not _API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in .env")

_client = genai.Client(api_key=_API_KEY)
_MODEL = "gemini-2.5-flash"


SYSTEM_PROMPT = """你是一個金融研究助理。你的任務是把使用者的中文/英文自然語言查詢，解析成結構化的因子研究參數。

可用的因子 (factor)：
- eps: 每股盈餘（月頻）
- revenue_growth: 營收年增率 (單位 %)（月頻）
- pe: 本益比（月頻）
- pb: 股價淨值比（月頻）

可用的特徵工程 (feature.type)：
- none: 直接用原始因子值
- growth_rate: 計算時序成長率（當使用者說「EPS 成長率」、「營收動能」時用這個）
- zscore: 時序 rolling z-score
- momentum: 最近 N 期的平均變化率

方向 (direction)：
- top: 取因子值最「高」的（例如「EPS 最高」、「成長最多」、「營收動能強」）
- bottom: 取因子值最「低」的（例如「最便宜」、「PE 最低」、「PB 最低」→ 低估值策略）

模式 (mode)：
- backtest: 使用者想看歷史績效、回測、報酬、Sharpe 等指標
- screen: 使用者想看當期選股名單、現在該買哪些

重要判斷：
1. 「低 PE」「便宜」「估值低」→ factor=pe, direction=bottom
2. 「高成長」「EPS 成長率」→ factor=eps, feature.type=growth_rate, direction=top
3. 「營收動能」→ factor=revenue_growth, feature.type=momentum, direction=top
4. 如果使用者沒明確說日期，預設 start=2018-01-01, end=2024-12-31
5. 如果使用者沒說要「回測」或「選股」，預設 backtest（除非說「現在」「目前」「最新」）
6. percentile 預設 20，使用者說「前 10%」就用 10，說「前三十檔」→ 先換算成百分比（約 6% for 台股）
7. explanation 欄位用**繁體中文**一句話說明你怎麼解析這個查詢

只回傳 JSON，不要其他文字。"""


RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "params": {
            "type": "object",
            "properties": {
                "mode": {"type": "string", "enum": ["backtest", "screen"]},
                "factor": {"type": "string", "enum": ["eps", "revenue_growth", "pe", "pb"]},
                "feature": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ["none", "growth_rate", "zscore", "momentum"]},
                        "window": {"type": "integer"},
                    },
                    "required": ["type", "window"],
                },
                "direction": {"type": "string", "enum": ["top", "bottom"]},
                "percentile": {"type": "number"},
                "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD"},
                "rebalance": {"type": "string", "enum": ["monthly"]},
            },
            "required": ["mode", "factor", "feature", "direction", "percentile", "start_date", "end_date", "rebalance"],
        },
        "explanation": {"type": "string"},
    },
    "required": ["params", "explanation"],
}


def parse_query(query: str) -> ParseResponse:
    """把自然語言查詢解析為 ParsedParams。"""
    response = _client.models.generate_content(
        model=_MODEL,
        contents=[query],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=RESPONSE_SCHEMA,
            temperature=0.1,
        ),
    )
    data = json.loads(response.text)
    return ParseResponse(
        params=ParsedParams(**data["params"]),
        explanation=data["explanation"],
    )
