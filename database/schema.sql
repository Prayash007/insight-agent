-- ============================================================================
-- InsightAgent: Capital Markets Schema (Angel One Retail Broking Domain)
-- Dialect: PostgreSQL 16 (Compatible with SQLite via standard DDL)
-- ============================================================================

-- Drop existing tables in dependency order
DROP TABLE IF EXISTS trades CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS instruments CASCADE;
DROP TABLE IF EXISTS clients CASCADE;

-- 1. Clients Table: Demat & Trading account holders
CREATE TABLE clients (
    client_id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    email VARCHAR(128) NOT NULL,
    tier VARCHAR(32) NOT NULL,            -- 'RETAIL', 'HNI', 'SUPER_HNI', 'INSTITUTIONAL'
    city VARCHAR(64) NOT NULL,
    state VARCHAR(64) NOT NULL,
    zone VARCHAR(32) NOT NULL,            -- 'NORTH', 'SOUTH', 'EAST', 'WEST'
    account_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE', -- 'ACTIVE', 'SUSPENDED', 'CLOSED'
    demat_active_flag BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL
);

-- 2. Instruments Master: Equity shares, index & stock options, and futures
CREATE TABLE instruments (
    instrument_id VARCHAR(32) PRIMARY KEY,
    tradingsymbol VARCHAR(64) NOT NULL,
    exchange VARCHAR(16) NOT NULL,        -- 'NSE', 'BSE', 'MCX'
    segment VARCHAR(32) NOT NULL,         -- 'EQUITY_CASH', 'FNO_OPTIONS', 'FNO_FUTURES', 'COMMODITY'
    instrument_type VARCHAR(16) NOT NULL, -- 'OPTIDX', 'OPTSTK', 'FUTIDX', 'FUTSTK', 'EQ'
    strike_price NUMERIC(12, 2),
    expiry_date DATE,
    lot_size INT NOT NULL DEFAULT 1,
    tick_size NUMERIC(6, 2) NOT NULL DEFAULT 0.05
);

-- 3. Orders Table: Ingested order book with RMS checks and execution status
CREATE TABLE orders (
    order_id VARCHAR(64) PRIMARY KEY,
    client_id VARCHAR(32) NOT NULL REFERENCES clients(client_id),
    instrument_id VARCHAR(32) NOT NULL REFERENCES instruments(instrument_id),
    transaction_type VARCHAR(8) NOT NULL, -- 'BUY', 'SELL'
    order_type VARCHAR(16) NOT NULL,       -- 'MARKET', 'LIMIT', 'SL'
    quantity INT NOT NULL,
    price NUMERIC(12, 2) NOT NULL,
    trigger_price NUMERIC(12, 2),
    status VARCHAR(16) NOT NULL,          -- 'COMPLETE', 'REJECTED', 'CANCELLED'
    rejection_reason VARCHAR(64) NOT NULL DEFAULT 'NONE', 
    -- 'RMS_INSUFFICIENT_MARGIN', 'CIRCUIT_LIMIT_BREACH', 'ORDER_LIMIT_EXCEEDED', 'EXCHANGE_CONNECTIVITY_DOWN', 'NONE'
    order_timestamp TIMESTAMP NOT NULL
);

-- 4. Trades Table: Executed order fills with financial yields and statutory taxes
CREATE TABLE trades (
    trade_id VARCHAR(64) PRIMARY KEY,
    order_id VARCHAR(64) NOT NULL REFERENCES orders(order_id),
    client_id VARCHAR(32) NOT NULL REFERENCES clients(client_id),
    instrument_id VARCHAR(32) NOT NULL REFERENCES instruments(instrument_id),
    traded_quantity INT NOT NULL,
    traded_price NUMERIC(12, 2) NOT NULL,
    turnover NUMERIC(14, 2) NOT NULL,
    brokerage_amount NUMERIC(10, 2) NOT NULL, -- Angel One brokerage yield (e.g. ₹20 flat on F&O)
    stt_tax NUMERIC(10, 2) NOT NULL,          -- Securities Transaction Tax
    exchange_turnover_fee NUMERIC(10, 2) NOT NULL,
    trade_timestamp TIMESTAMP NOT NULL
);

-- Performance & Analytical Indexes
CREATE INDEX idx_clients_tier ON clients(tier);
CREATE INDEX idx_clients_zone ON clients(zone);
CREATE INDEX idx_clients_created_at ON clients(created_at);

CREATE INDEX idx_instruments_segment ON instruments(segment);
CREATE INDEX idx_instruments_type ON instruments(instrument_type);
CREATE INDEX idx_instruments_expiry ON instruments(expiry_date);

CREATE INDEX idx_orders_client_id ON orders(client_id);
CREATE INDEX idx_orders_instrument_id ON orders(instrument_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_timestamp ON orders(order_timestamp);
CREATE INDEX idx_orders_rejection_reason ON orders(rejection_reason);

CREATE INDEX idx_trades_client_id ON trades(client_id);
CREATE INDEX idx_trades_instrument_id ON trades(instrument_id);
CREATE INDEX idx_trades_timestamp ON trades(trade_timestamp);
