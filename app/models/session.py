from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Session(Base):
    """對話視窗"""
    __tablename__ = "session"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    user_image = Column(String(500), nullable=True)
    gender_id = Column(Integer, ForeignKey("sex.id"), nullable=True)
    style_id = Column(Integer, ForeignKey("style_option.id"), nullable=True)
    detected_season_palette_id = Column(Integer, ForeignKey("season_palette.id"), nullable=True)
    skin_color_hex = Column(String(7), nullable=True)
    hair_color_hex = Column(String(7), nullable=True)
    eye_color = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 關聯
    user = relationship("User", back_populates="sessions")
    gender = relationship("Sex", back_populates="sessions")
    style = relationship("StyleOption", back_populates="sessions")
    detected_season = relationship("SeasonPalette", back_populates="sessions")
    rounds = relationship("Round", back_populates="session", cascade="all, delete-orphan")


class Round(Base):
    """推薦輪次"""
    __tablename__ = "round"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("session.id", ondelete="CASCADE"), nullable=False, index=True)
    selected_palette_ids = Column(JSONB, nullable=True)
    user_comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 關聯
    session = relationship("Session", back_populates="rounds")
    results = relationship("RoundRecommendedResult", back_populates="round", cascade="all, delete-orphan")


class RoundRecommendedResult(Base):
    """推薦結果"""
    __tablename__ = "round_recommended_result"
    
    id = Column(Integer, primary_key=True, index=True)
    round_id = Column(Integer, ForeignKey("round.id", ondelete="CASCADE"), nullable=False, index=True)
    image_id = Column(String(100), nullable=False)
    rank_order = Column(Integer, nullable=False)
    action_type_id = Column(Integer, ForeignKey("image_action.id"), nullable=True)
    dislike_desc = Column(Text, nullable=True)
    explanation_text = Column(Text, nullable=True)
    is_in_cart = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 關聯
    round = relationship("Round", back_populates="results")
    action_type = relationship("ImageAction", back_populates="results")


class Cart(Base):
    """購物車"""
    __tablename__ = "cart"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    image_id = Column(String(100), nullable=False)
    link = Column(String(500), nullable=True)
    update_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 關聯
    user = relationship("User", back_populates="carts")
