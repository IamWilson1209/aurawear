"""rename_tables_to_snake_case

Revision ID: 00de5ba60382
Revises: 
Create Date: 2026-02-15 20:06:44.869966

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00de5ba60382'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: Rename all tables from PascalCase to snake_case."""
    
    # Step 1: 刪除舊索引（因為索引名稱與表名相關）
    op.drop_index('idx_session_user', table_name='Session')
    op.drop_index('idx_round_session', table_name='Round')
    op.drop_index('idx_result_round', table_name='RoundRecommendedResult')
    op.drop_index('idx_cart_user', table_name='Cart')
    op.drop_index('idx_color_season_palette', table_name='Color')
    
    # Step 2: 重命名所有表（依照依賴順序：先重命名被依賴的表）
    op.rename_table('Sex', 'sex')
    op.rename_table('StyleOption', 'style_option')
    op.rename_table('SeasonPalette', 'season_palette')
    op.rename_table('Category', 'category')
    op.rename_table('ImageAction', 'image_action')
    op.rename_table('User', 'users')  # 使用複數形式
    op.rename_table('Color', 'color')
    op.rename_table('Session', 'session')
    op.rename_table('Round', 'round')
    op.rename_table('RoundRecommendedResult', 'round_recommended_result')
    op.rename_table('Cart', 'cart')
    
    # Step 3: 重新建立索引（使用新的表名）
    op.create_index('idx_session_user', 'session', ['user_id'])
    op.create_index('idx_round_session', 'round', ['session_id'])
    op.create_index('idx_result_round', 'round_recommended_result', ['round_id'])
    op.create_index('idx_cart_user', 'cart', ['user_id'])
    op.create_index('idx_color_season_palette', 'color', ['season_palette_id'])


def downgrade() -> None:
    """Downgrade schema: Rename all tables back from snake_case to PascalCase."""
    
    # Step 1: 刪除索引
    op.drop_index('idx_session_user', table_name='session')
    op.drop_index('idx_round_session', table_name='round')
    op.drop_index('idx_result_round', table_name='round_recommended_result')
    op.drop_index('idx_cart_user', table_name='cart')
    op.drop_index('idx_color_season_palette', table_name='color')
    
    # Step 2: 重命名回 PascalCase（反向操作）
    op.rename_table('cart', 'Cart')
    op.rename_table('round_recommended_result', 'RoundRecommendedResult')
    op.rename_table('round', 'Round')
    op.rename_table('session', 'Session')
    op.rename_table('color', 'Color')
    op.rename_table('users', 'User')
    op.rename_table('image_action', 'ImageAction')
    op.rename_table('category', 'Category')
    op.rename_table('season_palette', 'SeasonPalette')
    op.rename_table('style_option', 'StyleOption')
    op.rename_table('sex', 'Sex')
    
    # Step 3: 重新建立索引（使用舊的表名）
    op.create_index('idx_session_user', 'Session', ['user_id'])
    op.create_index('idx_round_session', 'Round', ['session_id'])
    op.create_index('idx_result_round', 'RoundRecommendedResult', ['round_id'])
    op.create_index('idx_cart_user', 'Cart', ['user_id'])
    op.create_index('idx_color_season_palette', 'Color', ['season_palette_id'])
