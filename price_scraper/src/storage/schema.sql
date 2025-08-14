-- Products table
CREATE TABLE IF NOT EXISTS products (
    id VARCHAR PRIMARY KEY,
    sku VARCHAR,
    name VARCHAR NOT NULL,
    brand VARCHAR,
    model VARCHAR,
    category VARCHAR,
    description TEXT,
    price DECIMAL(10,2),
    original_price DECIMAL(10,2),
    currency VARCHAR(3),
    status VARCHAR(20),
    stock_quantity INTEGER,
    site_name VARCHAR NOT NULL,
    url VARCHAR NOT NULL,
    image_urls JSON,
    extracted_at TIMESTAMP,
    last_updated TIMESTAMP,
    raw_data JSON,
    search_terms JSON,
    normalized_name VARCHAR
);

-- Price history table
CREATE TABLE IF NOT EXISTS price_history (
    id VARCHAR PRIMARY KEY,
    product_id VARCHAR,
    price DECIMAL(10,2),
    currency VARCHAR(3),
    extracted_at TIMESTAMP,
    site_name VARCHAR,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Product matches table (for cross-site product matching)
CREATE TABLE IF NOT EXISTS product_matches (
    id VARCHAR PRIMARY KEY,
    product_id_1 VARCHAR,
    product_id_2 VARCHAR,
    match_score DECIMAL(3,2),
    match_type VARCHAR(50),
    created_at TIMESTAMP,
    FOREIGN KEY (product_id_1) REFERENCES products(id),
    FOREIGN KEY (product_id_2) REFERENCES products(id)
);

-- Crawl sessions table
CREATE TABLE IF NOT EXISTS crawl_sessions (
    id VARCHAR PRIMARY KEY,
    site_name VARCHAR NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    products_found INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    status VARCHAR(20),
    metadata JSON
);

-- Exchange rates table
CREATE TABLE IF NOT EXISTS exchange_rates (
    id VARCHAR PRIMARY KEY,
    from_currency VARCHAR(3),
    to_currency VARCHAR(3),
    rate DECIMAL(10,6),
    updated_at TIMESTAMP,
    source VARCHAR(50)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_products_site_name ON products(site_name);
CREATE INDEX IF NOT EXISTS idx_products_brand_model ON products(brand, model);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_extracted_at ON products(extracted_at);
CREATE INDEX IF NOT EXISTS idx_price_history_product_id ON price_history(product_id);
CREATE INDEX IF NOT EXISTS idx_price_history_extracted_at ON price_history(extracted_at);
CREATE INDEX IF NOT EXISTS idx_exchange_rates_currencies ON exchange_rates(from_currency, to_currency);