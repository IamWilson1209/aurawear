CREATE TABLE Sex (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO Sex (name) VALUES 
    ('Male'),
    ('Female'),
    ('Unisex'),
    ('Untold');

CREATE TABLE StyleOption (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

INSERT INTO StyleOption (name) VALUES 
    ('Classic Tailoring'),
    ('Smart Casual / Workwear'),
    ('Minimalist / Clean'),
    ('Denim & Basics (Everyday Casual)'),
    ('Streetwear'),
    ('Edgy / Rock'),
    ('Avant-Garde / Fashion-Forward'),
    ('Athleisure'),
    ('Techwear / Gorpcore (Outdoor Functional)'),
    ('Bohemian');

-- SeasonPalette: 季節色分類，每個季節色包含 18 種顏色
CREATE TABLE SeasonPalette (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO SeasonPalette (name) VALUES 
    ('Light Spring'),
    ('True Spring'),
    ('Bright Spring'),
    ('Light Summer'),
    ('True Summer'),
    ('Soft Summer'),
    ('Soft Autumn'),
    ('True Autumn'),
    ('Deep Autumn'),
    ('Bright Winter'),
    ('True Winter'),
    ('Deep Winter');

CREATE TABLE Category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO Category (name) VALUES 
    ('top'),
    ('pants'),
    ('dress'),
    ('outer'),
    ('rompers'),
    ('skirt'),
    ('leggings');

CREATE TABLE ImageAction (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

INSERT INTO ImageAction (name) VALUES 
    ('LIKE'),
    ('DISLIKE'),
    ('ADD_TO_CART');

-- Color: 季節色顏色，每個 SeasonPalette 包含 18 種顏色
CREATE TABLE Color (
    id SERIAL PRIMARY KEY,
    season_palette_id INT NOT NULL REFERENCES SeasonPalette(id),
    color_code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    color_hex VARCHAR(7) NOT NULL
);

CREATE TABLE "User" (
    id VARCHAR(50) PRIMARY KEY,
    user_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Session (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    user_image VARCHAR(500),
    gender_id INT REFERENCES Sex(id),
    style_id INT REFERENCES StyleOption(id),
    detected_season_palette_id INT REFERENCES SeasonPalette(id),
    skin_color_hex VARCHAR(7),
    hair_color_hex VARCHAR(7),
    eye_color VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Round (
    id SERIAL PRIMARY KEY,
    session_id INT NOT NULL REFERENCES Session(id) ON DELETE CASCADE,
    selected_palette_ids JSONB,
    user_comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE RoundRecommendedResult (
    id SERIAL PRIMARY KEY,
    round_id INT NOT NULL REFERENCES Round(id) ON DELETE CASCADE,
    image_id VARCHAR(100) NOT NULL,
    rank_order INT NOT NULL,
    action_type_id INT REFERENCES ImageAction(id),
    dislike_desc TEXT,
    explanation_text TEXT,
    isInCart BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Cart (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    image_id VARCHAR(100) NOT NULL,
    link VARCHAR(500),
    update_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes (索引優化)
CREATE INDEX idx_session_user ON Session(user_id);
CREATE INDEX idx_round_session ON Round(session_id);
CREATE INDEX idx_result_round ON RoundRecommendedResult(round_id);
CREATE INDEX idx_cart_user ON Cart(user_id);
CREATE INDEX idx_color_season_palette ON Color(season_palette_id);

-- Grant Permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO aurawear_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO aurawear_user;