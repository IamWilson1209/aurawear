from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class CartAddRequest(BaseModel):
    """加入購物車請求"""
    user_id: str = Field(..., max_length=50, description="使用者 ID")
    image_id: str = Field(..., description="圖片 ID")
    link: str = Field(..., description="商品外部連結")


class CartItemResponse(BaseModel):
    """購物車項目回應"""
    id: int = Field(..., description="購物車項目 ID")
    user_id: str = Field(..., description="使用者 ID")
    image_id: str = Field(..., description="圖片 ID")
    link: str = Field(..., description="商品外部連結")
    update_at: datetime = Field(..., description="更新時間")

    class Config:
        from_attributes = True


class CartListResponse(BaseModel):
    """購物車列表回應"""
    items: List[CartItemResponse] = Field(..., description="購物車項目列表")
    total_count: int = Field(..., description="總數量")
