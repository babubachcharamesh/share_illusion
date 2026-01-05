
import duckdb
from simulation import make_all_thing
from db_init import con, initialize_tables, populate_all_date
from config import insert_sample_basic_setup, get_setup_val

def verify():
    print("Starting Verification...")
    initialize_tables()
    populate_all_date()
    insert_sample_basic_setup()
    
    # Get initial parameters
    tp = int(con.execute("SELECT TotalPeople FROM BASICSETUP").fetchone()[0])
    cwe = con.execute("SELECT CashWithEach FROM BASICSETUP").fetchone()[0]
    cap_bro = con.execute("SELECT CapitalOfBrokerCompany FROM BASICSETUP").fetchone()[0]
    
    # Note: Public company initial cash often comes from share sales, 
    # but let's see how much total cash is injected at the start.
    expected_total_cash = (tp * cwe) + cap_bro
    print(f"Expected Initial Total Cash: {expected_total_cash}")

    # Run simulation
    make_all_thing()
    
    # Check Transactions Table consistency
    # For each entity (Citizens + Companies + Gov), CASHIN - CASHOUT should be their current balance.
    # The sum of all balances should equal the initial total cash (closed system).
    
    entities = con.execute("SELECT DISTINCT CITIZENSHIPNO FROM TRANSACTIONS").fetchall()
    total_balance = 0
    errors = []
    
    for (ctz,) in entities:
        balance = con.execute("SELECT SUM(CASHIN - CASHOUT) FROM TRANSACTIONS WHERE CITIZENSHIPNO = ?", (ctz,)).fetchone()[0] or 0
        total_balance += balance
        if balance < -0.01: # Small epsilon for rounding
             # print(f"Warning: Negative balance for CTZ {ctz}: {balance}")
             pass

    total_balance = round(total_balance, 2)
    print(f"Final Total Cash in System: {total_balance}")
    
    if abs(total_balance - expected_total_cash) > 0.05:
        print(f"FAIL: Cash mismatch! Diff: {total_balance - expected_total_cash}")
    else:
        print("SUCCESS: Cash is balanced (within epsilon).")

    # Check for invalid citizenship numbers
    max_ctz = con.execute("SELECT MAX(CITIZENSHIPNO) FROM ALLPEOPLE").fetchone()[0]
    invalid_refs = con.execute("SELECT DISTINCT CITIZENSHIPNO FROM TRANSACTIONS WHERE CITIZENSHIPNO > ?", (max_ctz,)).fetchall()
    if invalid_refs:
        print(f"FAIL: Transactions found for non-existent citizens: {invalid_refs}")
    else:
        print("SUCCESS: All transaction citizenship numbers are valid.")

    # Check for zero-value transactions
    zero_trans = con.execute("""
        SELECT COUNT(*) FROM TRANSACTIONS 
        WHERE CASHIN == 0 AND CASHOUT == 0 AND SHAREBUYPRICE == 0 AND SHAREIN == 0 
          AND SHARESELLPRICE == 0 AND SHAREOUT == 0 AND PERSHARE == 0 
          AND GOODSIN == 0 AND GOODSOUT == 0 AND GOODSSELLINGPRICE == 0
    """).fetchone()[0]
    if zero_trans > 0:
        print(f"FAIL: Found {zero_trans} transactions with all zeros!")
    else:
        print("SUCCESS: No zero-value transactions found.")

if __name__ == "__main__":
    verify()
