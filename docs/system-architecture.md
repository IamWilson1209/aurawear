# AuraWear — System Architecture

## Overview

AuraWear 是一個基於 AI 的個人色彩分析與服飾推薦系統。使用者上傳個人照片後，系統透過 AI 模型分析出適合的季節色調色盤，再根據使用者偏好持續推薦服飾圖片。

### Tech Stack

| Layer               | Technology                                        |
| ------------------- | ------------------------------------------------- |
| **Frontend**        | TypeScript, Next.js, TailwindCSS, Shadcn          |
| **Backend Service** | Python, FastAPI, psycopg, PostgreSQL              |
| **AI Service**      | DS 團隊訓練的 AI Model, AstraDB (向量 + 圖片屬性) |

---

### 系統角色

| 角色                | 說明                                                                              |
| ------------------- | --------------------------------------------------------------------------------- |
| **Frontend**        | Next.js 前端應用，負責使用者互動與 UI 呈現                                        |
| **Backend Service** | FastAPI 後端服務，負責與前端溝通、管理 PostgreSQL 業務資料、轉發請求至 AI Service |
| **AI Service**      | 推薦演算法服務，負責接收使用者反饋、管理 AstraDB 向量資料、計算推薦結果           |
| **AI Model**        | DS 團隊訓練的深度學習模型，負責色彩分析與圖片 embedding                           |

---

## Flow 1 — 色彩分析（首頁：上傳照片）

使用者上傳個人照片，後端轉發至 AI Service，AI Model 分析出使用者的膚色、髮色、眼睛顏色，以及推薦的季節色調色盤（18 種顏色）。

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant BE as Backend Service
    participant AI as AI Service
    participant Model as AI Model

    FE ->> FE: 使用者點擊「開始」
    FE ->> FE: 使用者上傳個人照片

    FE ->>+ BE: POST /api/color-analysis<br/>payload: { image }
    BE ->>+ AI: 轉發照片至 AI Service
    AI ->>+ Model: 將圖片送入色彩分析模型
    Model -->>- AI: 回傳分析結果

    note over Model, AI: 分析結果包含：<br/>• season_12 (季節色分類)<br/>• skin_color_hex / hair_color_hex / eye_color<br/>• palette (18 種推薦顏色)

    AI -->>- BE: 回傳色彩分析 response
    BE -->>- FE: 回傳季節色調色盤 + 個人色彩資訊

    FE ->> FE: 顯示分析結果<br/>使用者可多選季節色 + 選擇性別 + 選擇風格
```

### 色彩分析 Response 結構

```json
{
  "season_12": "Light Spring",
  "season_hex": "#DADADA",
  "season_confidence": 0.82,
  "undertone": "warm",
  "skin_color_hex": "#D4A574",
  "hair_color_hex": "#4A3728",
  "eye_color": "brown",
  "eye_color_hex": "#6B4226",
  "eye_color_confidence": 0.75,
  "palette": [
    {"id": "ls_01", "hex": "#FFB7A5", "name": "Peach Blossom", "season": "Light Spring"},
    ...
  ]
}
```

---

## Flow 2 — 建立 Session 與初次推薦（進入主介面）

使用者確認選定的季節色、性別與風格後，後端建立 Session + 第一個 Round，並向 AI Service 請求初次推薦。

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant BE as Backend Service
    participant AI as AI Service
    participant Model as AI Model

    FE ->> FE: 使用者多選季節色 + 選擇性別 + 選擇風格

    FE ->>+ BE: POST /api/sessions<br/>payload: { selected_palette_ids, gender, style,<br/>user_image, skin_color_hex, hair_color_hex, eye_color }

    BE ->> BE: 建立 Session 記錄 (PostgreSQL)
    BE ->> BE: 建立 Round #1 記錄 (PostgreSQL)

    BE ->>+ AI: POST /recommend<br/>payload: { images, selected_palette_ids,<br/>filters: { styles, gender }, k: 50 }

    AI ->>+ Model: 使用推薦演算法<br/>計算所有圖片排序分數
    Model -->>- AI: 回傳計算結果

    AI ->> AI: 排序圖片、取 Top 50

    note over AI: 將 round 向量寫入 AstraDB<br/>(Round Vector Collection)

    AI -->>- BE: 回傳推薦圖片 Top 50 (含分數、說明)

    BE ->> BE: 儲存 Round Recommended Result (PostgreSQL)
    BE -->>- FE: 回傳推薦結果 (50張推薦圖片)

    FE ->> FE: 顯示主介面<br/>照片、性別、風格、季節色調色盤 + 推薦圖片
    FE ->> FE: disable「重新生成」按鈕
```

---

## Flow 3 — 使用者互動操作（Round 內）

在一個 Round 內，使用者可以對推薦圖片進行操作、更新留言、變更調色盤顏色。這些操作會記錄在前端，直到使用者按下「重新生成」。

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant BE as Backend Service

    note over FE: 「重新生成」按鈕預設 disabled<br/>直到以下任一行為發生

    alt 操作一：圖片互動
        FE ->> FE: 點擊「喜歡」圖片
        FE ->> FE: enable「重新生成」按鈕
    end

    alt 操作二：不喜歡圖片
        FE ->> FE: 點擊「不喜歡」圖片
        FE ->> FE: 彈出描述輸入框（可選填）
        FE ->> FE: enable「重新生成」按鈕
    end

    alt 操作三：加入購物車
        FE ->>+ BE: POST /api/cart<br/>payload: { user_id, image_id, link }
        BE ->> BE: 寫入 Cart 記錄 (PostgreSQL)
        BE -->>- FE: 確認加入購物車
    end

    alt 操作四：變更季節色調色盤
        FE ->> FE: 更新選擇的季節色
        FE ->> FE: enable「重新生成」按鈕
    end

    alt 操作五：更新留言
        FE ->> FE: 輸入/更新留言<br/>例：「我想要更嘻哈一點的風格」
        FE ->> FE: enable「重新生成」按鈕
    end
```

---

## Flow 4 — Regenerate 重新推薦

使用者按下「重新生成」按鈕後，前端彙整該 Round 的所有互動資料，送出至後端，觸發 AI Service 重新計算推薦排序。

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant BE as Backend Service
    participant AI as AI Service
    participant Model as AI Model

    FE ->> FE: 使用者按下「重新生成」按鈕

    FE ->>+ BE: POST /api/sessions/{sid}/rounds<br/>payload: {<br/>  selected_palette_ids,<br/>  like: [image_id, ...],<br/>  dislike: [{image_id, comment}, ...],<br/>  previous_round: [image_id, ...],<br/>  user_text: "我想要更嘻哈一點的風格",<br/>  k: 50<br/>}

    BE ->> BE: 建立新 Round 記錄 (PostgreSQL)
    BE ->> BE: 更新前一輪圖片的 action_type<br/>(like / dislike / dislike_desc)

    BE ->>+ AI: POST /recommend<br/>payload: { 完整推薦 request }

    AI ->>+ Model: 重新拉取「所有圖片」<br/>根據新偏好重新計算排序
    Model -->>- AI: 回傳計算結果

    AI ->> AI: 排序圖片、取 Top 50

    note over AI: 寫入新的 Round Vector<br/>至 AstraDB (Round Vector Collection)

    AI -->>- BE: 回傳重新推薦結果 Top 50

    alt AstraDB 寫入成功
        BE ->> BE: 儲存 Round Recommended Result (PostgreSQL)
        BE -->>- FE: 回傳新推薦結果
        FE ->> FE: 刷新推薦列表
        FE ->> FE: disable「重新生成」按鈕
    end

    note over BE: ⚠️ Rollback 處理見 Flow 5
```

---

## Flow 5 — Rollback 機制

為確保 PostgreSQL 與 AstraDB 之間的資料一致性，採用 **PostgreSQL 優先** 的寫入策略。

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant BE as Backend Service
    participant PG as PostgreSQL
    participant AI as AI Service
    participant Astra as AstraDB

    FE ->>+ BE: Regenerate 請求

    BE ->>+ PG: Step 1: 寫入 Round + Recommended Result
    PG -->>- BE: PostgreSQL 寫入成功

    BE ->>+ AI: Step 2: 請求推薦 + 寫入向量
    AI ->>+ Astra: 寫入 Round Vector Collection

    alt AstraDB 寫入成功
        Astra -->>- AI: 寫入成功
        AI -->>- BE: 推薦結果 + 向量寫入完成
        BE -->>- FE: 回傳推薦結果
    end

    alt AstraDB 寫入失敗
        Astra -->> AI: 寫入失敗
        AI -->> BE: 回傳錯誤

        BE ->>+ PG: Step 3: Rollback — 刪除該次 Round 記錄
        PG -->>- BE: Rollback 完成

        BE -->> FE: 回傳錯誤訊息<br/>提示使用者重試
    end
```

---

## Flow 6 — 購物車操作

購物車以使用者（User）為單位，跨所有 Session 收集使用者加入的圖片。

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant BE as Backend Service

    note over FE: 購物車頁面（以 User 為單位）

    alt 查看購物車
        FE ->>+ BE: GET /api/cart?user_id={uid}
        BE -->>- FE: 回傳該使用者所有購物車項目<br/>(跨所有 Session，含 image_id, link, update_at)
        FE ->> FE: 顯示購物車清單
    end

    alt 點擊商品外部連結
        FE ->> FE: 開啟外部網站<br/>查看商品詳細資訊
    end

    alt 從購物車移除
        FE ->>+ BE: DELETE /api/cart/{cart_id}
        BE ->> BE: 刪除 Cart 記錄 (PostgreSQL)
        BE -->>- FE: 移除成功
        FE ->> FE: 更新購物車顯示
    end
```

---

## 完整系統流程總覽

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant BE as Backend Service
    participant AI as AI Service
    participant Model as AI Model

        note over FE, Model: 📷 Phase 1 — 色彩分析（首頁）
        FE ->> BE: 上傳個人照片
        BE ->> AI: 轉發照片
        AI ->> Model: 色彩分析
        Model -->> AI: 季節色 + 膚色/髮色/眼色
        AI -->> BE: 分析結果 + 18 色調色盤
        BE -->> FE: 回傳色彩分析結果

    FE ->> FE: 選擇季節色 + 性別 + 風格

        note over FE, Model: 🎨 Phase 2 — 建立 Session & 初次推薦
        FE ->> BE: 建立 Session + 初次推薦請求
        BE ->> BE: 建立 Session / Round (PostgreSQL)
        BE ->> AI: 推薦請求 (k=50)
        AI ->> Model: 推薦演算法計算
        Model -->> AI: 圖片排序結果
        AI -->> BE: Top 50 推薦圖片
        BE -->> FE: 推薦結果

        note over FE, Model: 🔄 Phase 3 — 互動 & Regenerate（可重複多次）
        FE ->> FE: 使用者操作：喜歡/不喜歡/留言/換色

        FE ->> BE: Regenerate 請求 (新 Round)
        BE ->> BE: 建立新 Round (PostgreSQL)
        BE ->> AI: 推薦請求 (含使用者反饋)
        AI ->> Model: 重新計算排序
        Model -->> AI: 更新後的排序結果
        AI -->> BE: 新 Top 50 推薦
        BE -->> FE: 新推薦結果

        note over FE, BE: 🛒 Phase 4 — 購物車
        FE ->> BE: 加入 / 移除購物車
        BE -->> FE: 確認操作結果
```

---

## API Endpoints 概覽

| Method   | Endpoint                     | 說明                                         |
| -------- | ---------------------------- | -------------------------------------------- |
| `POST`   | `/api/color-analysis`        | 上傳照片進行色彩分析                         |
| `POST`   | `/api/sessions`              | 建立 Session + 初次推薦                      |
| `POST`   | `/api/sessions/{sid}/rounds` | Regenerate — 建立新 Round                    |
| `GET`    | `/api/cart?user_id={uid}`    | 查看購物車（以 User 為單位，跨所有 Session） |
| `POST`   | `/api/cart`                  | 加入購物車                                   |
| `DELETE` | `/api/cart/{cart_id}`        | 從購物車移除                                 |

---

## 非功能性設計要點

- **資料一致性**：採用 PostgreSQL 優先寫入策略，AstraDB 失敗時 Rollback PostgreSQL 記錄
- **推薦機制**：每次推薦回傳 50 張圖片，依分數由高到低排序
- **Regenerate 觸發條件**：變更季節色 / 喜歡或不喜歡圖片 / 更新留言，三者至少符合一項才 enable
- **Round 機制**：每次 Regenerate 產生一個新 Round，完整記錄使用者偏好變化軌跡
- **購物車**：以 User 為單位，跨所有 Session 彙整使用者加入的圖片
