from fastapi import APIRouter, HTTPException, status
from app.schemas.color_analysis import ColorAnalysisRequest, ColorAnalysisResponse
import httpx

router = APIRouter()

# AI Service URL - 應該從環境變數讀取
AI_SERVICE_URL = "http://ai-service:8001"  # 需要配置


@router.post("/color-analysis", response_model=ColorAnalysisResponse)
async def analyze_color(request: ColorAnalysisRequest):
    """
    色彩分析 API
    
    上傳個人照片，轉發至 AI Service 進行色彩分析，
    回傳季節色、膚色/髮色/眼色、以及 18 色調色盤。
    """
    try:
        # 轉發請求至 AI Service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_SERVICE_URL}/analyze-color",
                json={"image": request.image},
                timeout=30.0
            )
            response.raise_for_status()
            
        return ColorAnalysisResponse(**response.json())
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"AI Service error: {e.response.text}"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to AI Service: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
