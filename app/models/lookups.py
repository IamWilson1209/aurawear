from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Sex(Base):
    """性別選項"""
    __tablename__ = "sex"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    
    # 關聯
    sessions = relationship("Session", back_populates="gender")


class StyleOption(Base):
    """風格選項"""
    __tablename__ = "style_option"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    
    # 關聯
    sessions = relationship("Session", back_populates="style")


class SeasonPalette(Base):
    """季節色分類"""
    __tablename__ = "season_palette"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    
    # 關聯
    colors = relationship("Color", back_populates="season_palette")
    sessions = relationship("Session", back_populates="detected_season")


class Category(Base):
    """衣物分類"""
    __tablename__ = "category"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)


class ImageAction(Base):
    """圖片操作類型"""
    __tablename__ = "image_action"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    
    # 關聯
    results = relationship("RoundRecommendedResult", back_populates="action_type")


class Color(Base):
    """季節色顏色"""
    __tablename__ = "color"
    
    id = Column(Integer, primary_key=True, index=True)
    season_palette_id = Column(Integer, ForeignKey("season_palette.id"), nullable=False)
    color_code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    color_hex = Column(String(7), nullable=False)
    
    # 關聯
    season_palette = relationship("SeasonPalette", back_populates="colors")
