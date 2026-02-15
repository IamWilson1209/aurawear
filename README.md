# AuraWear Backend API

這是 AuraWear 個人色彩診斷系統的後端 API 服務。

## 技術棧

- **FastAPI** - 現代化的 Python Web 框架
- **PostgreSQL** - 關聯式資料庫
- **SQLAlchemy 2.0** - ORM（Object-Relational Mapping）
- **Alembic** - 資料庫遷移工具
- **Pydantic** - 資料驗證與序列化
- **Docker** - 容器化資料庫服務

## 專案架構

```
aurawear-backend/
├── app/
│   ├── models/          # SQLAlchemy ORM 模型
│   │   ├── lookups.py   # 查找表（Sex, StyleOption, SeasonPalette, Category, ImageAction, Color）
│   │   ├── user.py      # User 模型
│   │   └── session.py   # Session, Round, RoundRecommendedResult, Cart 模型
│   ├── schemas/         # Pydantic 驗證 schemas
│   │   ├── user.py      # User 相關 schemas
│   │   ├── color.py     # Color 與 SeasonPalette schemas
│   │   └── session.py   # Session 相關 schemas
│   ├── repositories/    # Repository Pattern 資料存取層
│   │   ├── user.py      # UserRepository
│   │   ├── color.py     # ColorRepository, SeasonPaletteRepository
│   │   └── session.py   # SessionRepository, RoundRepository, CartRepository
│   ├── routers/         # API 路由
│   │   └── v1/
│   │       ├── users.py    # User CRUD endpoints
│   │       ├── colors.py   # Color & SeasonPalette endpoints（唯讀）
│   │       └── sessions.py # Session CRUD endpoints
│   ├── config.py        # Pydantic Settings 配置
│   ├── database.py      # SQLAlchemy 資料庫連線設定
│   └── main.py          # FastAPI 應用程式進入點
├── migrations/          # Alembic 資料庫遷移腳本
├── docker/              # Docker 初始化腳本
├── constants/           # 常數資料（color.json）
├── scripts/             # 工具腳本
├── docker-compose.yml   # Docker Compose 配置
├── alembic.ini          # Alembic 配置
├── requirements.txt     # Python 套件依賴
└── .env                 # 環境變數（請勿提交到 Git）
```

## 快速開始

### 1. 啟動資料庫

```bash
# 啟動 PostgreSQL 和 pgAdmin
docker-compose up -d
```

資料庫連線資訊：

- 主機: `localhost`
- 埠號: `5432`
- 資料庫名稱: `aurawear_db`
- 使用者: `aurawear_user`
- 密碼: `aurawear_pass_2026`

pgAdmin Web UI:

- URL: http://localhost:5050
- Email: `admin@aurawear.com`
- Password: `admin_2026`

### 2. 建立 Python 虛擬環境

```bash
# 建立虛擬環境
python3 -m venv venv

# 啟動虛擬環境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安裝依賴套件
pip install -r requirements.txt
```

### 3. 執行資料庫遷移

```bash
# 升級到最新版本
alembic upgrade head

# 檢查遷移狀態
alembic current
```

### 4. 啟動 API 伺服器

```bash
# 開發模式（支援熱重載）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 服務：

- API 根路徑: http://localhost:8000/
- 互動式文件（Swagger UI）: http://localhost:8000/docs
- 替代文件（ReDoc）: http://localhost:8000/redoc
- 健康檢查: http://localhost:8000/health

## API 端點

### Users（使用者）

- `POST /api/v1/users/` - 建立使用者
- `GET /api/v1/users/{user_id}` - 取得使用者資訊
- `GET /api/v1/users/` - 取得使用者列表
- `PUT /api/v1/users/{user_id}` - 更新使用者資訊
- `DELETE /api/v1/users/{user_id}` - 刪除使用者

### Colors（顏色與季節色盤）

- `GET /api/v1/colors/palettes` - 取得所有季節色盤（不含顏色）
- `GET /api/v1/colors/palettes/with-colors` - 取得所有季節色盤（含顏色）
- `GET /api/v1/colors/palettes/{palette_id}` - 取得單一季節色盤
- `GET /api/v1/colors/palettes/{palette_id}/with-colors` - 取得單一季節色盤（含顏色）
- `GET /api/v1/colors/palettes/{palette_id}/colors` - 取得指定季節色盤的所有顏色
- `GET /api/v1/colors/colors` - 取得顏色列表
- `GET /api/v1/colors/colors/{color_id}` - 取得單一顏色資訊

### Sessions（診斷對話）

- `POST /api/v1/sessions/` - 建立診斷 Session
- `GET /api/v1/sessions/{session_id}` - 取得 Session 資訊
- `GET /api/v1/sessions/user/{user_id}` - 取得使用者的所有 Sessions
- `PUT /api/v1/sessions/{session_id}` - 更新 Session 資訊
- `DELETE /api/v1/sessions/{session_id}` - 刪除 Session

## 範例請求

### 建立使用者

```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": "user_001",
    "user_name": "Christine"
  }'
```

### 取得所有季節色盤（含顏色）

```bash
curl http://localhost:8000/api/v1/colors/palettes/with-colors
```

### 建立診斷 Session

```bash
curl -X POST http://localhost:8000/api/v1/sessions/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "user_image": "uploads/user_001_photo.jpg",
    "gender_id": 1,
    "style_id": 5,
    "detected_season_id": 1,
    "skin_color_hex": "#D4A574",
    "hair_color_hex": "#4A3728"
  }'
```

## 開發工具

### Alembic 資料庫遷移

```bash
# 檢查當前版本
alembic current

# 查看遷移歷史
alembic history

# 升級到最新版本
alembic upgrade head

# 降級一個版本
alembic downgrade -1

# 生成新的遷移腳本
alembic revision --autogenerate -m "描述變更內容"

# 查看遷移狀態
alembic show head
```

### Prisma Studio（資料庫視覺化工具 - 可選）

如果已安裝 Prisma：

```bash
prisma studio
```

## 環境變數

在專案根目錄建立 `.env` 檔案：

```env
# Database
DATABASE_URL=postgresql://aurawear_user:aurawear_pass_2026@localhost:5432/aurawear_db

# API
PROJECT_NAME=AuraWear API
VERSION=1.0.0
API_V1_PREFIX=/api/v1
```

## 資料庫說明

### 資料表

1. **users** - 使用者資料
2. **session** - 診斷對話
3. **round** - 推薦輪次
4. **round_recommended_result** - 推薦結果
5. **cart** - 購物車
6. **sex** - 性別查找表
7. **style_option** - 風格查找表
8. **season_palette** - 季節色盤查找表（12 種）
9. **category** - 商品分類查找表
10. **image_action** - 圖片操作查找表
11. **color** - 顏色資料（216 筆，每個 SeasonPalette 18 種顏色）

### 初始資料

- **12 個 SeasonPalette**（Light Spring, True Spring, Bright Spring, Light Summer, True Summer, Soft Summer, Soft Autumn, True Autumn, Deep Autumn, Bright Winter, True Winter, Deep Winter）
- **216 個 Color**（每個 SeasonPalette 18 種顏色）

資料在 Docker 容器啟動時會自動匯入（透過 `docker/postgres/init.sql`）。

## 測試

訪問 http://localhost:8000/docs 使用 Swagger UI 進行互動式 API 測試。

## 生產部署

1. 更新 `.env` 中的資料庫連線資訊
2. 設定 `echo=False` 在 `database.py` 中（已預設）
3. 使用生產級 ASGI 伺服器：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

或使用 Gunicorn + Uvicorn workers：

```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 授權

此專案為 AuraWear 個人色彩診斷系統的一部分。
