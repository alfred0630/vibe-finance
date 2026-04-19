"""POST /parse - 把自然語言轉成 ParsedParams"""
from fastapi import APIRouter, HTTPException
from ..schemas import ParseRequest, ParseResponse
from ..gemini import parse_query

router = APIRouter()


@router.post("/parse", response_model=ParseResponse)
def parse(req: ParseRequest) -> ParseResponse:
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="query cannot be empty")
    try:
        return parse_query(req.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini parse error: {e}")
