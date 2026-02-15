import json
import os
from collections import defaultdict

def generate_color_sql():
    """從 constants/color.json 生成 SQL INSERT 語句"""
    
    # 季節色映射 (對應 SeasonPalette 表的 id)
    SEASON_PALETTE_MAP = {
        "Light Spring": 1,
        "True Spring": 2,
        "Bright Spring": 3,
        "Light Summer": 4,
        "True Summer": 5,
        "Soft Summer": 6,
        "Soft Autumn": 7,
        "True Autumn": 8,
        "Deep Autumn": 9,
        "Bright Winter": 10,
        "True Winter": 11,
        "Deep Winter": 12
    }
    
    # 讀取 color.json (專案根目錄的 constants/color.json)
    color_file = os.path.join(os.path.dirname(__file__), "..", "constants", "color.json")
    
    with open(color_file, "r", encoding="utf-8") as f:
        colors = json.load(f)
    
    # 統計每個季節色的顏色數量
    season_count = defaultdict(int)
    
    # 生成 SQL
    sql_statements = [
        "-- ============================================",
        "-- Import Color Data from constants/color.json",
        "-- 每個 SeasonPalette 應包含 18 種顏色",
        "-- ============================================\n"
    ]
    
    for color in colors:
        season_palette_id = SEASON_PALETTE_MAP[color["season"]]
        name = color["name"].replace("'", "''")  # 轉義單引號
        
        sql = f"INSERT INTO Color (season_palette_id, color_code, name, color_hex) VALUES ({season_palette_id}, '{color['id']}', '{name}', '{color['hex']}');"
        sql_statements.append(sql)
        
        # 統計
        season_count[color["season"]] += 1
    
    # 寫入 SQL 檔案
    output_dir = os.path.join(os.path.dirname(__file__), "..", "docker", "postgres")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "import_colors.sql")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_statements))
    
    print(f"✅ Generated {len(colors)} color INSERT statements")
    print(f"📁 Output: {output_path}")
    print("\n📊 SeasonPalette 顏色統計 (每個季節色應有 18 種顏色):")
    print("-" * 50)
    
    for season_name in SEASON_PALETTE_MAP.keys():
        count = season_count[season_name]
        status = "✅" if count == 18 else "⚠️"
        print(f"{status} {season_name:20s} : {count:2d} 種顏色")
    
    print("-" * 50)
    print(f"📈 總計: {len(colors)} 種顏色")
    
    # 檢查是否所有季節色都有 18 種顏色
    if all(count == 18 for count in season_count.values()):
        print("\n🎉 完美！所有 SeasonPalette 都包含 18 種顏色")
    else:
        print("\n⚠️  警告：部分 SeasonPalette 的顏色數量不足或超過 18 種")

if __name__ == "__main__":
    generate_color_sql()