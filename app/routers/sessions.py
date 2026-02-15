from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.schemas.session import (
    SessionCreateRequest,
    SessionCreateResponse,
    RoundCreateRequest,
    RoundCreateResponse,
    RecommendedImage
)
from app.repositories.session import (
    SessionRepository,
    RoundRepository,
    RoundRecommendedResultRepository
)
from app.models.user import User
import httpx

router = APIRouter()

# AI Service URL - 應該從環境變數讀取
AI_SERVICE_URL = "http://ai-service:8001"  # 需要配置


@router.post("/sessions", response_model=SessionCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_session(request: SessionCreateRequest, db: DBSession = Depends(get_db)):
    """
    建立 Session + 初次推薦
    
    使用者選定季節色、性別與風格後，建立 Session 和第一個 Round，
    向 AI Service 請求初次推薦，回傳 Top K 推薦圖片。
    """
    # 1. 檢查使用者是否存在
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 2. 建立 Session
    session = SessionRepository.create_session(
        db=db,
        user_id=request.user_id,
        user_image=request.user_image,
        gender_id=request.gender_id,
        style_id=request.style_id,
        skin_color_hex=request.skin_color_hex,
        hair_color_hex=request.hair_color_hex,
        eye_color=request.eye_color
    )
    
    # 3. 建立第一個 Round
    round_obj = RoundRepository.create_round(
        db=db,
        session_id=session.id,
        selected_palette_ids=request.selected_palette_ids
    )
    
    # 4. 向 AI Service 請求推薦
    try:
        async with httpx.AsyncClient() as client:
            ai_response = await client.post(
                f"{AI_SERVICE_URL}/recommend",
                json={
                    "selected_palette_ids": request.selected_palette_ids,
                    "filters": {
                        "gender": request.gender_id,
                        "styles": [request.style_id]
                    },
                    "k": request.k
                },
                timeout=60.0
            )
            ai_response.raise_for_status()
            ai_data = ai_response.json()
        
        # 5. 儲存推薦結果到資料庫
        recommended_images = ai_data.get("recommended_images", [])
        RoundRecommendedResultRepository.bulk_create_results(
            db=db,
            round_id=round_obj.id,
            recommended_images=recommended_images
        )
        
        # 6. 回傳結果
        return SessionCreateResponse(
            session_id=session.id,
            round_id=round_obj.id,
            recommended_images=[
                RecommendedImage(**img) for img in recommended_images
            ]
        )
    
    except httpx.HTTPStatusError as e:
        # AI Service 錯誤，刪除已建立的 Session 和 Round
        RoundRepository.delete_round(db, round_obj.id)
        db.delete(session)
        db.commit()
        
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"AI Service error: {e.response.text}"
        )
    
    except Exception as e:
        # 其他錯誤，刪除已建立的 Session 和 Round
        RoundRepository.delete_round(db, round_obj.id)
        db.delete(session)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@router.post("/sessions/{session_id}/rounds", response_model=RoundCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_round(
    session_id: int,
    request: RoundCreateRequest,
    db: DBSession = Depends(get_db)
):
    """
    Regenerate — 建立新 Round
    
    使用者按下「重新生成」後，建立新 Round，更新前一輪圖片的操作記錄，
    向 AI Service 請求重新推薦，回傳新的 Top K 推薦圖片。
    
    若 AstraDB 寫入失敗，執行 Rollback 刪除該次 Round 記錄。
    """
    # 1. 檢查 Session 是否存在
    session = SessionRepository.get_by_id(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # 2. 建立新 Round
    round_obj = RoundRepository.create_round(
        db=db,
        session_id=session_id,
        selected_palette_ids=request.selected_palette_ids,
        user_comment=request.user_text
    )
    
    # 3. 更新前一輪圖片的 action_type（like / dislike）
    # 假設 action_type_id: 1=like, 2=dislike
    for image_id in request.like:
        # 需要找到前一輪的 round_id，這裡簡化處理
        # 實際應該從 request 或 session 中取得前一輪的 round_id
        pass  # TODO: 實作更新前一輪的 action
    
    for dislike_item in request.dislike:
        # 更新 dislike 的圖片
        pass  # TODO: 實作更新前一輪的 action
    
    # 4. 向 AI Service 請求重新推薦
    try:
        async with httpx.AsyncClient() as client:
            ai_response = await client.post(
                f"{AI_SERVICE_URL}/recommend",
                json={
                    "selected_palette_ids": request.selected_palette_ids,
                    "like": request.like,
                    "dislike": request.dislike,
                    "previous_round": request.previous_round,
                    "user_text": request.user_text,
                    "k": request.k,
                    "session_id": session_id,
                    "round_id": round_obj.id
                },
                timeout=60.0
            )
            ai_response.raise_for_status()
            ai_data = ai_response.json()
        
        # 5. 檢查 AstraDB 是否寫入成功
        if not ai_data.get("vector_saved", True):
            # AstraDB 寫入失敗，執行 Rollback
            RoundRepository.delete_round(db, round_obj.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save round vector to AstraDB. Please retry."
            )
        
        # 6. 儲存推薦結果到資料庫
        recommended_images = ai_data.get("recommended_images", [])
        RoundRecommendedResultRepository.bulk_create_results(
            db=db,
            round_id=round_obj.id,
            recommended_images=recommended_images
        )
        
        # 7. 回傳結果
        return RoundCreateResponse(
            round_id=round_obj.id,
            recommended_images=[
                RecommendedImage(**img) for img in recommended_images
            ]
        )
    
    except httpx.HTTPStatusError as e:
        # AI Service 錯誤，Rollback
        RoundRepository.delete_round(db, round_obj.id)
        
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"AI Service error: {e.response.text}"
        )
    
    except Exception as e:
        # 其他錯誤，Rollback
        RoundRepository.delete_round(db, round_obj.id)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create round: {str(e)}"
        )
