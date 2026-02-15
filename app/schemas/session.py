from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class SessionCreateRequest(BaseModel):
    """建立 Session 請求"""
    user_id: str = Field(..., max_length=50, description="使用者 ID")
    selected_palette_ids: List[int] = Field(..., description="選擇的季節色盤 ID 列表")
    gender_id: int = Field(..., description="性別 ID")
    style_id: int = Field(..., description="風格 ID")
    user_image: str = Field(..., description="使用者上傳的照片路徑")
    skin_color_hex: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$", description="膚色色碼")
    hair_color_hex: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$", description="髮色色碼")
    eye_color: Optional[str] = Field(None, description="眼睛顏色")
    k: int = Field(50, ge=1, le=100, description="推薦圖片數量")


class RecommendedImage(BaseModel):
    """推薦圖片"""
    image_id: str = Field(..., description="圖片 ID")
    rank_order: int = Field(..., description="排序順位")
    score: float = Field(..., description="推薦分數")
    explanation_text: Optional[str] = Field(None, description="推薦說明")


class SessionCreateResponse(BaseModel):
    """建立 Session 回應"""
    session_id: int = Field(..., description="Session ID")
    round_id: int = Field(..., description="第一個 Round ID")
    recommended_images: List[RecommendedImage] = Field(..., description="推薦圖片列表")


class RoundCreateRequest(BaseModel):
    """建立新 Round 請求（Regenerate）"""
    selected_palette_ids: List[int] = Field(..., description="選擇的季節色盤 ID 列表")
    like: List[str] = Field(default_factory=list, description="喜歡的圖片 ID 列表")
    dislike: List[dict] = Field(default_factory=list, description="不喜歡的圖片（含評論）")
    previous_round: List[str] = Field(..., description="上一輪的圖片 ID 列表")
    user_text: Optional[str] = Field(None, description="使用者留言")
    k: int = Field(50, ge=1, le=100, description="推薦圖片數量")


class RoundCreateResponse(BaseModel):
    """建立新 Round 回應"""
    round_id: int = Field(..., description="新 Round ID")
    recommended_images: List[RecommendedImage] = Field(..., description="推薦圖片列表")
