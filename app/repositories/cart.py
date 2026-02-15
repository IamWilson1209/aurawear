from typing import List, Optional
from sqlalchemy.orm import Session as DBSession
from app.models.session import Cart


class CartRepository:
    """購物車資料存取層"""

    @staticmethod
    def add_to_cart(
        db: DBSession,
        user_id: str,
        image_id: str,
        link: str
    ) -> Cart:
        """加入購物車"""
        # 檢查是否已存在
        existing = db.query(Cart).filter(
            Cart.user_id == user_id,
            Cart.image_id == image_id
        ).first()
        
        if existing:
            # 更新連結和時間
            existing.link = link
            db.commit()
            db.refresh(existing)
            return existing
        
        # 新增
        cart_item = Cart(
            user_id=user_id,
            image_id=image_id,
            link=link
        )
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
        return cart_item

    @staticmethod
    def get_user_cart(db: DBSession, user_id: str) -> List[Cart]:
        """取得使用者購物車"""
        return db.query(Cart).filter(Cart.user_id == user_id).order_by(Cart.update_at.desc()).all()

    @staticmethod
    def remove_from_cart(db: DBSession, cart_id: int) -> bool:
        """從購物車移除"""
        cart_item = db.query(Cart).filter(Cart.id == cart_id).first()
        if not cart_item:
            return False
        
        db.delete(cart_item)
        db.commit()
        return True

    @staticmethod
    def get_by_id(db: DBSession, cart_id: int) -> Optional[Cart]:
        """根據 ID 取得購物車項目"""
        return db.query(Cart).filter(Cart.id == cart_id).first()
