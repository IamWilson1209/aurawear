from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.schemas.cart import CartAddRequest, CartItemResponse, CartListResponse
from app.repositories.cart import CartRepository

router = APIRouter()


@router.get("/cart", response_model=CartListResponse)
def get_user_cart(user_id: str = Query(..., description="使用者 ID"), db: DBSession = Depends(get_db)):
    """
    查看購物車
    
    以使用者為單位，回傳該使用者所有購物車項目（跨所有 Session）。
    """
    cart_items = CartRepository.get_user_cart(db, user_id)
    
    return CartListResponse(
        items=[CartItemResponse.model_validate(item) for item in cart_items],
        total_count=len(cart_items)
    )


@router.post("/cart", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(request: CartAddRequest, db: DBSession = Depends(get_db)):
    """
    加入購物車
    
    將指定的圖片加入使用者的購物車。
    若已存在則更新連結和時間。
    """
    cart_item = CartRepository.add_to_cart(
        db=db,
        user_id=request.user_id,
        image_id=request.image_id,
        link=request.link
    )
    
    return CartItemResponse.model_validate(cart_item)


@router.delete("/cart/{cart_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(cart_id: int, db: DBSession = Depends(get_db)):
    """
    從購物車移除
    
    從購物車中刪除指定的項目。
    """
    success = CartRepository.remove_from_cart(db, cart_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
