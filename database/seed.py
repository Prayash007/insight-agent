"""
InsightAgent: Synthetic Capital Markets Data Generator (Angel One Retail Broking Domain)
Populates 25,000 clients and 250,000 orders/trades with injected market anomalies:
  1. August F&O Turnover Contraction (-28% drop in Options turnover vs July)
  2. August 14 Peak Margin Rejection Surge (14x spike in RMS_INSUFFICIENT_MARGIN)
  3. Thursday Expiry Trading Surges (3.2x concentration in index options)
"""

import os
import sys
import json
import random
import argparse
from datetime import datetime, date, timedelta
from pathlib import Path
import numpy as np
from sqlalchemy import create_engine, text

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Set random seed for deterministic reproducibility across benchmark runs
np.random.seed(42)
random.seed(42)

# Default DB URL: Check env or fallback to local SQLite for zero-config development
DEFAULT_DB_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'database' / 'insight_brokerage.db'}")


def get_db_engine(db_url: str):
    """Creates an engine configured for Postgres or SQLite."""
    if db_url.startswith("sqlite"):
        return create_engine(db_url, echo=False)
    else:
        return create_engine(db_url, pool_pre_ping=True, echo=False)


def init_schema(engine):
    """Executes DDL schema on target database."""
    schema_file = BASE_DIR / "database" / "schema.sql"
    with open(schema_file, "r", encoding="utf-8") as f:
        ddl_script = f.read()

    # If SQLite, adjust Postgres-specific keywords
    if engine.dialect.name == "sqlite":
        # SQLite doesn't support CASCADE or NUMERIC precision syntax in quite the same way, but standard SQL runs fine
        ddl_script = ddl_script.replace("CASCADE", "")

    with engine.begin() as conn:
        for stmt in ddl_script.split(";"):
            cleaned = stmt.strip()
            if cleaned:
                conn.execute(text(cleaned))
    print("Schema initialized successfully.")


INDIAN_CITIES = [
    ("Mumbai", "Maharashtra", "WEST"),
    ("Pune", "Maharashtra", "WEST"),
    ("Ahmedabad", "Gujarat", "WEST"),
    ("Surat", "Gujarat", "WEST"),
    ("Delhi", "Delhi", "NORTH"),
    ("Jaipur", "Rajasthan", "NORTH"),
    ("Lucknow", "Uttar Pradesh", "NORTH"),
    ("Chandigarh", "Punjab", "NORTH"),
    ("Bangalore", "Karnataka", "SOUTH"),
    ("Hyderabad", "Telangana", "SOUTH"),
    ("Chennai", "Tamil Nadu", "SOUTH"),
    ("Kochi", "Kerala", "SOUTH"),
    ("Kolkata", "West Bengal", "EAST"),
    ("Patna", "Bihar", "EAST"),
    ("Bhubaneswar", "Odisha", "EAST"),
]

TIERS = ["RETAIL", "HNI", "SUPER_HNI", "INSTITUTIONAL"]
TIER_WEIGHTS = [0.82, 0.13, 0.04, 0.01]

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
    "Shaurya", "Atharv", "Dhruv", "Kabir", "Rudra", "Aryan", "Ananya", "Diya", "Saanvi", "Aadhya",
    "Pari", "Chiara", "Riya", "Myra", "Anushka", "Aarohi", "Isha", "Kavya", "Prisha", "Tanvi",
    "Rahul", "Rohan", "Pooja", "Vikram", "Neha", "Amit", "Sneha", "Karan", "Priya", "Sunil"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Shah", "Mehta", "Joshi", "Gupta", "Agarwal", "Singh", "Kumar",
    "Mishra", "Reddy", "Nair", "Iyer", "Rao", "Chauhan", "Bhatia", "Deshmukh", "Kulkarni", "Banerjee"
]


def generate_clients(n=25000):
    """Generates synthetic client demographic profiles."""
    clients = []
    base_date = datetime(2023, 1, 1)

    for i in range(1, n + 1):
        client_id = f"CL_{i:05d}"
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}{i}@example.com"
        tier = random.choices(TIERS, weights=TIER_WEIGHTS, k=1)[0]
        city, state, zone = random.choice(INDIAN_CITIES)
        created_at = base_date + timedelta(days=random.randint(0, 500), hours=random.randint(9, 17))
        account_status = random.choices(["ACTIVE", "SUSPENDED", "CLOSED"], weights=[0.96, 0.03, 0.01], k=1)[0]
        demat_active = True if account_status == "ACTIVE" and random.random() < 0.95 else False

        clients.append({
            "client_id": client_id,
            "name": name,
            "email": email,
            "tier": tier,
            "city": city,
            "state": state,
            "zone": zone,
            "account_status": account_status,
            "demat_active_flag": demat_active,
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return clients


def generate_instruments():
    """Generates capital markets instruments master (NSE/BSE/MCX)."""
    instruments = []

    # 1. Equity Cash
    cash_stocks = [
        ("RELIANCE", 2950.0), ("TCS", 4250.0), ("HDFCBANK", 1650.0), ("INFY", 1880.0),
        ("ICICIBANK", 1240.0), ("TATAMOTORS", 1020.0), ("SBIN", 840.0), ("ITC", 495.0),
        ("BHARTIARTL", 1560.0), ("ANGELONE", 2750.0), ("LT", 3620.0), ("BAJFINANCE", 7100.0)
    ]
    ins_idx = 1
    for symbol, base_price in cash_stocks:
        instruments.append({
            "instrument_id": f"INS_{ins_idx:04d}",
            "tradingsymbol": symbol,
            "exchange": "NSE",
            "segment": "EQUITY_CASH",
            "instrument_type": "EQ",
            "strike_price": None,
            "expiry_date": None,
            "lot_size": 1,
            "tick_size": 0.05
        })
        ins_idx += 1

    # 2. Index Options (Nifty & BankNifty across strikes)
    expiries = [
        date(2024, 8, 1), date(2024, 8, 8), date(2024, 8, 14), date(2024, 8, 22), date(2024, 8, 29),
        date(2024, 7, 4), date(2024, 7, 11), date(2024, 7, 18), date(2024, 7, 25),
        date(2024, 9, 5), date(2024, 9, 12), date(2024, 9, 19), date(2024, 9, 26)
    ]
    for exp in expiries:
        # Nifty Options
        for strike in [24000, 24200, 24500, 24800, 25000]:
            for opt_type in ["CE", "PE"]:
                instruments.append({
                    "instrument_id": f"INS_{ins_idx:04d}",
                    "tradingsymbol": f"NIFTY{exp.strftime('%y%b').upper()}{strike}{opt_type}",
                    "exchange": "NSE",
                    "segment": "FNO_OPTIONS",
                    "instrument_type": "OPTIDX",
                    "strike_price": strike,
                    "expiry_date": exp.strftime("%Y-%m-%d"),
                    "lot_size": 25,
                    "tick_size": 0.05
                })
                ins_idx += 1

        # BankNifty Options
        for strike in [49500, 50000, 50500, 51000, 51500]:
            for opt_type in ["CE", "PE"]:
                instruments.append({
                    "instrument_id": f"INS_{ins_idx:04d}",
                    "tradingsymbol": f"BANKNIFTY{exp.strftime('%y%b').upper()}{strike}{opt_type}",
                    "exchange": "NSE",
                    "segment": "FNO_OPTIONS",
                    "instrument_type": "OPTIDX",
                    "strike_price": strike,
                    "expiry_date": exp.strftime("%Y-%m-%d"),
                    "lot_size": 15,
                    "tick_size": 0.05
                })
                ins_idx += 1

    # 3. Stock Options
    for exp in [date(2024, 7, 25), date(2024, 8, 29), date(2024, 9, 26)]:
        for symbol, strike, lot in [("RELIANCE", 3000, 250), ("TCS", 4300, 175), ("TATAMOTORS", 1050, 550)]:
            for opt_type in ["CE", "PE"]:
                instruments.append({
                    "instrument_id": f"INS_{ins_idx:04d}",
                    "tradingsymbol": f"{symbol}{exp.strftime('%y%b').upper()}{strike}{opt_type}",
                    "exchange": "NSE",
                    "segment": "FNO_OPTIONS",
                    "instrument_type": "OPTSTK",
                    "strike_price": strike,
                    "expiry_date": exp.strftime("%Y-%m-%d"),
                    "lot_size": lot,
                    "tick_size": 0.05
                })
                ins_idx += 1

    # 4. Futures
    for exp in [date(2024, 7, 25), date(2024, 8, 29), date(2024, 9, 26)]:
        instruments.append({
            "instrument_id": f"INS_{ins_idx:04d}",
            "tradingsymbol": f"NIFTY{exp.strftime('%y%b').upper()}FUT",
            "exchange": "NSE",
            "segment": "FNO_FUTURES",
            "instrument_type": "FUTIDX",
            "strike_price": None,
            "expiry_date": exp.strftime("%Y-%m-%d"),
            "lot_size": 25,
            "tick_size": 0.05
        })
        ins_idx += 1
        instruments.append({
            "instrument_id": f"INS_{ins_idx:04d}",
            "tradingsymbol": f"BANKNIFTY{exp.strftime('%y%b').upper()}FUT",
            "exchange": "NSE",
            "segment": "FNO_FUTURES",
            "instrument_type": "FUTIDX",
            "strike_price": None,
            "expiry_date": exp.strftime("%Y-%m-%d"),
            "lot_size": 15,
            "tick_size": 0.05
        })
        ins_idx += 1

    # 5. Commodities
    for comm, lot, price in [("CRUDEOIL", 100, 6400), ("GOLD", 100, 72000), ("SILVER", 30, 84000)]:
        instruments.append({
            "instrument_id": f"INS_{ins_idx:04d}",
            "tradingsymbol": f"{comm}24AUGFUT",
            "exchange": "MCX",
            "segment": "COMMODITY",
            "instrument_type": "FUTSTK",
            "strike_price": None,
            "expiry_date": "2024-08-20",
            "lot_size": lot,
            "tick_size": 1.0
        })
        ins_idx += 1

    return instruments


def generate_orders_and_trades(clients, instruments, target_orders=250000):
    """
    Generates orders and executed trades with targeted business anomalies:
      - August F&O volume drop (-28% options turnover vs July)
      - August 14 RMS rejection spike (35% rejections vs 2.5% baseline)
      - Thursday expiry surge (3.2x concentration in options)
    """
    orders = []
    trades = []

    client_ids = [c["client_id"] for c in clients if c["demat_active_flag"]]
    opt_instruments = [ins for ins in instruments if ins["segment"] == "FNO_OPTIONS"]
    fut_instruments = [ins for ins in instruments if ins["segment"] == "FNO_FUTURES"]
    eq_instruments = [ins for ins in instruments if ins["segment"] == "EQUITY_CASH"]
    comm_instruments = [ins for ins in instruments if ins["segment"] == "COMMODITY"]

    # Date range: March 1, 2024 to October 31, 2024 (245 days)
    start_date = date(2024, 3, 1)
    end_date = date(2024, 10, 31)
    total_days = (end_date - start_date).days

    order_counter = 1
    trade_counter = 1

    # Pre-generate day distribution
    print(f"Generating {target_orders} orders and trades across {total_days} days...")
    
    # Target approximately target_orders across valid trading days (Monday to Friday)
    trading_days = []
    curr = start_date
    while curr <= end_date:
        if curr.weekday() < 5:  # 0=Mon, ..., 4=Fri
            trading_days.append(curr)
        curr += timedelta(days=1)

    num_trading_days = len(trading_days)
    base_orders_per_day = target_orders // num_trading_days

    for trading_day in trading_days:
        day_of_week = trading_day.weekday() # 3 is Thursday
        is_thursday = (day_of_week == 3)
        is_august = (trading_day.month == 8)
        is_august_14 = (trading_day == date(2024, 8, 14))

        # Determine daily order volume with anomalies
        multiplier = 1.0
        if is_thursday:
            multiplier *= 1.85  # Thursday expiry concentration

        if is_august:
            multiplier *= 0.82  # August overall retail volume slowdown

        day_order_count = int(base_orders_per_day * multiplier * random.uniform(0.92, 1.08))

        for _ in range(day_order_count):
            if order_counter > target_orders:
                break

            order_id = f"ORD_{order_counter:08d}"
            client_id = random.choice(client_ids)
            
            # Segment choice:
            # Baseline: Options 68%, Equity 20%, Futures 8%, Commodity 4%
            # If August: Options share drops to ~52% (28% decline in turnover)
            # If Thursday: Options share surges to 84%
            if is_thursday:
                segment_weights = [0.84, 0.09, 0.05, 0.02]
            elif is_august:
                segment_weights = [0.52, 0.32, 0.11, 0.05]
            else:
                segment_weights = [0.68, 0.20, 0.08, 0.04]

            chosen_pool = random.choices(
                [opt_instruments, eq_instruments, fut_instruments, comm_instruments],
                weights=segment_weights,
                k=1
            )[0]
            ins = random.choice(chosen_pool)
            instrument_id = ins["instrument_id"]

            txn_type = random.choice(["BUY", "SELL"])
            order_type = random.choices(["MARKET", "LIMIT", "SL"], weights=[0.60, 0.32, 0.08], k=1)[0]

            # Price and quantity based on instrument type
            lot_size = ins["lot_size"]
            lots = random.choices([1, 2, 4, 10, 25], weights=[0.45, 0.25, 0.18, 0.09, 0.03], k=1)[0]
            quantity = lots * lot_size

            if ins["segment"] == "FNO_OPTIONS":
                # Option premium (between ₹15 and ₹350)
                price = round(random.uniform(25.0, 320.0), 2)
            elif ins["segment"] == "EQUITY_CASH":
                price = round(random.uniform(150.0, 3500.0), 2)
            elif ins["segment"] == "FNO_FUTURES":
                price = round(random.uniform(22000.0, 52000.0), 2)
            else:
                price = round(random.uniform(4000.0, 75000.0), 2)

            trigger_price = round(price * 0.98, 2) if order_type == "SL" else None

            # Execution status & rejection reasons
            # Normal rejection rate: ~4% total, ~2.5% RMS margin
            # On August 14: Rejection rate spikes to ~35% with RMS_INSUFFICIENT_MARGIN
            if is_august_14:
                status_roll = random.random()
                if status_roll < 0.35:
                    status = "REJECTED"
                    rejection_reason = "RMS_INSUFFICIENT_MARGIN"
                elif status_roll < 0.40:
                    status = "CANCELLED"
                    rejection_reason = "NONE"
                else:
                    status = "COMPLETE"
                    rejection_reason = "NONE"
            else:
                status_roll = random.random()
                if status_roll < 0.038:
                    status = "REJECTED"
                    rejection_reason = random.choices(
                        ["RMS_INSUFFICIENT_MARGIN", "CIRCUIT_LIMIT_BREACH", "ORDER_LIMIT_EXCEEDED", "EXCHANGE_CONNECTIVITY_DOWN"],
                        weights=[0.68, 0.15, 0.12, 0.05],
                        k=1
                    )[0]
                elif status_roll < 0.065:
                    status = "CANCELLED"
                    rejection_reason = "NONE"
                else:
                    status = "COMPLETE"
                    rejection_reason = "NONE"

            # Market hours: 09:15:00 to 15:30:00 IST
            hour = random.choices([9, 10, 11, 12, 13, 14, 15], weights=[0.24, 0.14, 0.10, 0.09, 0.11, 0.14, 0.18], k=1)[0]
            minute = random.randint(0, 59) if hour != 9 and hour != 15 else (random.randint(15, 59) if hour == 9 else random.randint(0, 30))
            second = random.randint(0, 59)
            order_time = datetime.combine(trading_day, datetime.min.time()) + timedelta(hours=hour, minutes=minute, seconds=second)

            orders.append({
                "order_id": order_id,
                "client_id": client_id,
                "instrument_id": instrument_id,
                "transaction_type": txn_type,
                "order_type": order_type,
                "quantity": quantity,
                "price": price,
                "trigger_price": trigger_price,
                "status": status,
                "rejection_reason": rejection_reason,
                "order_timestamp": order_time.strftime("%Y-%m-%d %H:%M:%S")
            })

            # If order filled successfully, create trade record
            if status == "COMPLETE":
                trade_id = f"TRD_{trade_counter:08d}"
                traded_qty = quantity
                traded_price = price
                turnover = round(traded_qty * traded_price, 2)

                # Angel One brokerage model: flat ₹20 on F&O/Commodity, delivery 0.1% max ₹20
                if ins["segment"] in ["FNO_OPTIONS", "FNO_FUTURES", "COMMODITY"]:
                    brokerage = 20.0
                else:
                    brokerage = min(20.0, round(turnover * 0.001, 2))

                # Statutory taxes (STT & Exchange turnover fee)
                stt_tax = round(turnover * 0.000625, 2) if ins["segment"] == "FNO_OPTIONS" else round(turnover * 0.001, 2)
                exchange_fee = round(turnover * 0.000035, 2)
                trade_time = order_time + timedelta(milliseconds=random.randint(12, 450))

                trades.append({
                    "trade_id": trade_id,
                    "order_id": order_id,
                    "client_id": client_id,
                    "instrument_id": instrument_id,
                    "traded_quantity": traded_qty,
                    "traded_price": traded_price,
                    "turnover": turnover,
                    "brokerage_amount": brokerage,
                    "stt_tax": stt_tax,
                    "exchange_turnover_fee": exchange_fee,
                    "trade_timestamp": trade_time.strftime("%Y-%m-%d %H:%M:%S")
                })
                trade_counter += 1

            order_counter += 1

    return orders, trades


def bulk_insert(engine, table_name, records, batch_size=5000):
    """Inserts records in chunks using SQLAlchemy."""
    print(f"Inserting {len(records)} records into '{table_name}'...")
    if not records:
        return

    with engine.begin() as conn:
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            col_names = list(batch[0].keys())
            placeholders = ", ".join([f":{col}" for col in col_names])
            cols_clause = ", ".join(col_names)
            sql = f"INSERT INTO {table_name} ({cols_clause}) VALUES ({placeholders})"
            conn.execute(text(sql), batch)
            sys.stdout.write(f"\r  Progress: {min(i + batch_size, len(records))}/{len(records)} rows")
            sys.stdout.flush()
    print(f"\nCompleted insert into '{table_name}'.")


def verify_anomalies(engine):
    """Prints verification statistics of the injected capital market anomalies."""
    print("\n" + "=" * 60)
    print("INSIGHTAGENT: ANOMALY VERIFICATION SUITE")
    print("=" * 60)

    with engine.connect() as conn:
        # 1. August vs July F&O Options Turnover
        q1 = """
        SELECT 
            strftime('%Y-%m', t.trade_timestamp) as month,
            COUNT(*) as trade_count,
            ROUND(SUM(t.turnover), 2) as total_turnover
        FROM trades t
        JOIN instruments i ON t.instrument_id = i.instrument_id
        WHERE i.segment = 'FNO_OPTIONS' AND strftime('%Y-%m', t.trade_timestamp) IN ('2024-07', '2024-08')
        GROUP BY month
        ORDER BY month
        """
        # If Postgres, use TO_CHAR
        if engine.dialect.name == "postgresql":
            q1 = q1.replace("strftime('%Y-%m', t.trade_timestamp)", "TO_CHAR(t.trade_timestamp, 'YYYY-MM')")

        res1 = conn.execute(text(q1)).fetchall()
        print("\n[1] F&O Options Turnover (July vs August Anomaly Check):")
        july_turnover = 0
        aug_turnover = 0
        for r in res1:
            print(f"  Month: {r[0]} | Trades: {r[1]:,} | Turnover: Rs. {r[2]:,.2f}")
            if "07" in str(r[0]):
                july_turnover = r[2]
            elif "08" in str(r[0]):
                aug_turnover = r[2]

        if july_turnover > 0:
            pct_change = ((aug_turnover - july_turnover) / july_turnover) * 100
            print(f"  --> Delta: {pct_change:.2f}% (Target: ~-28%)")

        # 2. August 14 RMS Rejection Spike
        q2 = """
        SELECT 
            DATE(order_timestamp) as o_date,
            COUNT(*) as total_orders,
            COUNT(CASE WHEN status = 'REJECTED' AND rejection_reason = 'RMS_INSUFFICIENT_MARGIN' THEN 1 END) as rms_rejections,
            ROUND((COUNT(CASE WHEN status = 'REJECTED' AND rejection_reason = 'RMS_INSUFFICIENT_MARGIN' THEN 1 END) * 100.0) / COUNT(*), 2) as rms_pct
        FROM orders
        WHERE DATE(order_timestamp) BETWEEN '2024-08-12' AND '2024-08-16'
        GROUP BY o_date
        ORDER BY o_date
        """
        if engine.dialect.name == "postgresql":
            q2 = q2.replace("DATE(order_timestamp)", "order_timestamp::DATE")

        res2 = conn.execute(text(q2)).fetchall()
        print("\n[2] August 14 RMS Rejection Spike Check:")
        for r in res2:
            star = " <--- SPIKE DETECTED" if "08-14" in str(r[0]) else ""
            print(f"  Date: {r[0]} | Orders: {r[1]:,} | RMS Rejections: {r[2]:,} ({r[3]}%){star}")

        # 3. Thursday Expiry Surge
        print("\n[3] Thursday vs Weekday Options Volume Check:")
        q3 = """
        SELECT 
            CASE CAST(strftime('%w', t.trade_timestamp) AS INTEGER)
                WHEN 1 THEN 'Monday'
                WHEN 2 THEN 'Tuesday'
                WHEN 3 THEN 'Wednesday'
                WHEN 4 THEN 'Thursday'
                WHEN 5 THEN 'Friday'
                ELSE 'Weekend'
            END as weekday_name,
            COUNT(*) as trade_count,
            ROUND(SUM(t.turnover), 2) as turnover
        FROM trades t
        JOIN instruments i ON t.instrument_id = i.instrument_id
        WHERE i.segment = 'FNO_OPTIONS'
        GROUP BY weekday_name
        ORDER BY turnover DESC
        """
        if engine.dialect.name == "postgresql":
            q3 = """
            SELECT 
                TO_CHAR(t.trade_timestamp, 'Day') as weekday_name,
                COUNT(*) as trade_count,
                ROUND(SUM(t.turnover), 2) as turnover
            FROM trades t
            JOIN instruments i ON t.instrument_id = i.instrument_id
            WHERE i.segment = 'FNO_OPTIONS'
            GROUP BY weekday_name
            ORDER BY turnover DESC
            """
        res3 = conn.execute(text(q3)).fetchall()
        for r in res3:
            print(f"  {str(r[0]).strip():12} | Trades: {r[1]:,} | Turnover: Rs. {r[2]:,.2f}")

    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Seed capital markets database for InsightAgent")
    parser.add_argument("--db-url", type=str, default=DEFAULT_DB_URL, help="Database connection URL")
    parser.add_argument("--clients", type=int, default=25000, help="Number of clients to generate")
    parser.add_argument("--orders", type=int, default=250000, help="Number of orders to generate")
    parser.add_argument("--verify-only", action="store_true", help="Only run anomaly verification")
    args = parser.parse_args()

    engine = get_db_engine(args.db_url)

    if args.verify_only:
        verify_anomalies(engine)
        return

    print(f"Target Database: {args.db_url}")
    init_schema(engine)

    clients = generate_clients(n=args.clients)
    bulk_insert(engine, "clients", clients)

    instruments = generate_instruments()
    bulk_insert(engine, "instruments", instruments)

    orders, trades = generate_orders_and_trades(clients, instruments, target_orders=args.orders)
    bulk_insert(engine, "orders", orders)
    bulk_insert(engine, "trades", trades)

    verify_anomalies(engine)
    print("Database seeding completed successfully.")


if __name__ == "__main__":
    main()
