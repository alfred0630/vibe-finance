"""POST /research - 執行因子研究（回測 or 選股）"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from ..schemas import ResearchRequest
from ..factor_engine import run_research

router = APIRouter()


@router.post("/research")
def research(req: ResearchRequest):
    try:
        result = run_research(req.params)
        # model_dump(mode="json") 確保 date 序列化為字串且 params 完整保留
        return JSONResponse(content=result.model_dump(mode="json"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engine error: {e}")
