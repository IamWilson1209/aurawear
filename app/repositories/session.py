from typing import Optional, List
from sqlalchemy.orm import Session as DBSession
from app.models.session import Session, Round, RoundRecommendedResult


class SessionRepository:
    """Session 資料存取層"""

    @staticmethod
    def create_session(
        db: DBSession,
        user_id: str,
        user_image: str,
        gender_id: int,
        style_id: int,
        skin_color_hex: str,
        hair_color_hex: str,
        eye_color: Optional[str] = None,
        detected_season_palette_id: Optional[int] = None
    ) -> Session:
        """建立 Session"""
        session = Session(
            user_id=user_id,
            user_image=user_image,
            gender_id=gender_id,
            style_id=style_id,
            skin_color_hex=skin_color_hex,
            hair_color_hex=hair_color_hex,
            eye_color=eye_color,
            detected_season_palette_id=detected_season_palette_id
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_by_id(db: DBSession, session_id: int) -> Optional[Session]:
        """根據 ID 取得 Session"""
        return db.query(Session).filter(Session.id == session_id).first()


class RoundRepository:
    """Round 資料存取層"""

    @staticmethod
    def create_round(
        db: DBSession,
        session_id: int,
        selected_palette_ids: List[int],
        user_comment: Optional[str] = None
    ) -> Round:
        """建立 Round"""
        round_obj = Round(
            session_id=session_id,
            selected_palette_ids=selected_palette_ids,
            user_comment=user_comment
        )
        db.add(round_obj)
        db.commit()
        db.refresh(round_obj)
        return round_obj

    @staticmethod
    def delete_round(db: DBSession, round_id: int) -> bool:
        """刪除 Round（用於 Rollback）"""
        round_obj = db.query(Round).filter(Round.id == round_id).first()
        if not round_obj:
            return False
        db.delete(round_obj)
        db.commit()
        return True


class RoundRecommendedResultRepository:
    """Round 推薦結果資料存取層"""

    @staticmethod
    def create_result(
        db: DBSession,
        round_id: int,
        image_id: str,
        rank_order: int,
        explanation_text: Optional[str] = None,
        action_type_id: Optional[int] = None,
        dislike_desc: Optional[str] = None,
        is_in_cart: bool = False
    ) -> RoundRecommendedResult:
        """建立推薦結果"""
        result = RoundRecommendedResult(
            round_id=round_id,
            image_id=image_id,
            rank_order=rank_order,
            explanation_text=explanation_text,
            action_type_id=action_type_id,
            dislike_desc=dislike_desc,
            is_in_cart=is_in_cart
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        return result

    @staticmethod
    def bulk_create_results(
        db: DBSession,
        round_id: int,
        recommended_images: List[dict]
    ) -> List[RoundRecommendedResult]:
        """批次建立推薦結果"""
        results = []
        for img in recommended_images:
            result = RoundRecommendedResult(
                round_id=round_id,
                image_id=img["image_id"],
                rank_order=img["rank_order"],
                explanation_text=img.get("explanation_text")
            )
            results.append(result)
        
        db.bulk_save_objects(results)
        db.commit()
        return results

    @staticmethod
    def update_action(
        db: DBSession,
        round_id: int,
        image_id: str,
        action_type_id: int,
        dislike_desc: Optional[str] = None
    ) -> Optional[RoundRecommendedResult]:
        """更新推薦結果的使用者操作"""
        result = db.query(RoundRecommendedResult).filter(
            RoundRecommendedResult.round_id == round_id,
            RoundRecommendedResult.image_id == image_id
        ).first()
        
        if result:
            result.action_type_id = action_type_id
            if dislike_desc:
                result.dislike_desc = dislike_desc
            db.commit()
            db.refresh(result)
        
        return result
