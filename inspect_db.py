"""
Inspect Railway PostgreSQL database tables.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: Set DATABASE_URL environment variable first.")
    sys.exit(1)

try:
    import psycopg2
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

url = DATABASE_URL.replace("postgres://", "postgresql://", 1)

try:
    conn = psycopg2.connect(url)
    cur = conn.cursor()
    print("[OK] Connected to PostgreSQL successfully!\n")
except Exception as e:
    print(f"[FAIL] Connection failed: {e}")
    sys.exit(1)

# List all tables
cur.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public' ORDER BY table_name
""")
tables = [row[0] for row in cur.fetchall()]
print(f"Tables found: {tables}\n")
print("=" * 80)

for table in tables:
    # Get column names
    cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position")
    columns = [row[0] for row in cur.fetchall()]
    
    # Get row count
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    count = cur.fetchone()[0]
    
    print(f"\nTable: {table} ({count} rows)")
    print(f"  Columns: {', '.join(columns)}")
    print("-" * 80)
    
    # Show data (limit to 20 rows)
    cur.execute(f"SELECT * FROM {table} ORDER BY id DESC LIMIT 20")
    rows = cur.fetchall()
    
    if not rows:
        print("  (empty)")
        continue
    
    # Print header
    col_widths = []
    for i, col in enumerate(columns):
        max_w = len(col)
        for row in rows:
            val = str(row[i]) if row[i] is not None else "NULL"
            # Replace non-ASCII chars for Windows console
            val = val.encode('ascii', 'replace').decode('ascii')
            max_w = max(max_w, min(len(val), 40))
        col_widths.append(min(max_w, 40))
    
    header = " | ".join(col.ljust(w) for col, w in zip(columns, col_widths))
    print(f"  {header}")
    print(f"  {'-+-'.join('-' * w for w in col_widths)}")
    
    for row in rows:
        vals = []
        for i, val in enumerate(row):
            s = str(val) if val is not None else "NULL"
            s = s.encode('ascii', 'replace').decode('ascii')
            if len(s) > 40:
                s = s[:37] + "..."
            vals.append(s.ljust(col_widths[i]))
        print(f"  {' | '.join(vals)}")
    
    if count > 20:
        print(f"  ... and {count - 20} more rows")

print("\n" + "=" * 80)
print("Done!")
cur.close()
conn.close()
