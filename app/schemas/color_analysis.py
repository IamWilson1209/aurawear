from pydantic import BaseModel, Field
from typing import List


class PaletteColor(BaseModel):
    """調色盤顏色"""
    id: str = Field(..., description="顏色 ID，如 ls_01")
    hex: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$", description="十六進制色碼")
    name: str = Field(..., description="顏色名稱")
    season: str = Field(..., description="季節色名稱")


class ColorAnalysisRequest(BaseModel):
    """色彩分析請求"""
    image: str = Field(..., description="圖片 Base64 編碼或 URL")


class ColorAnalysisResponse(BaseModel):
    """色彩分析回應"""
    season_12: str = Field(..., description="12 季節色分類")
    season_hex: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$", description="季節色代表色碼")
    season_confidence: float = Field(..., ge=0, le=1, description="季節色信心度")
    undertone: str = Field(..., description="冷暖調性")
    skin_color_hex: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$", description="膚色色碼")
    hair_color_hex: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$", description="髮色色碼")
    eye_color: str = Field(..., description="眼睛顏色")
    eye_color_hex: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$", description="眼睛顏色色碼")
    eye_color_confidence: float = Field(..., ge=0, le=1, description="眼色信心度")
    palette: List[PaletteColor] = Field(..., description="推薦的 18 色調色盤")
