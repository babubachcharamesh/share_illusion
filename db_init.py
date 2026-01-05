import duckdb
from datetime import datetime, timedelta

con = duckdb.connect(':memory:')

def initialize_tables():
    con.execute("""
        CREATE TABLE IF NOT EXISTS BASICSETUP (
            GeneralPublic INTEGER, TotalPeople INTEGER, CashWithEach DOUBLE, PromotorsOfBrokerCompany INTEGER, CapitalOfBrokerCompany DOUBLE,
            PromotorsOfPublicCompany INTEGER, ParValueOfShare DOUBLE, PublicCompanyNoOfShares INTEGER, PublicHolding DOUBLE,
            PublicCompanyPublicShareholders INTEGER, BrokerageRate DOUBLE, CapitalGainTaxRate DOUBLE, ProfitMarginDaily DOUBLE,
            GovernmentEmployees INTEGER, BrokerCompanyEmployees INTEGER, PublicCompanyEmployees INTEGER,
            GovernmentEmployeesSalary DOUBLE, BrokerCompanyEmployeesSalary DOUBLE, PublicCompanyEmployeesSalary DOUBLE,
            PersonalTaxRate DOUBLE, PerDayProduction DOUBLE, DividendExpected DOUBLE, CorporateTaxRate DOUBLE,
            WorkingDays INTEGER, PublicCompanyEmployeesSalaryMonths INTEGER
        )
    """)
    con.execute("CREATE TABLE IF NOT EXISTS ALLPEOPLE (CITIZENSHIPNO INTEGER, CASHBALANCE DOUBLE, EMPLOYER VARCHAR, EMPLOYERCTZN INTEGER)")
    con.execute("CREATE TABLE IF NOT EXISTS SHARELIST (CITIZENSHIPNO INTEGER, COMPANYNAME VARCHAR, PROMOTORSHARE DOUBLE, PUBLICSHARE DOUBLE)")
    con.execute("""
        CREATE TABLE IF NOT EXISTS TRANSACTIONS (TRANDATES DATE, CITIZENSHIPNO INTEGER, TRANSDETAIL VARCHAR, CASHIN DOUBLE, CASHOUT DOUBLE,
            SHAREBUYPRICE DOUBLE, SHAREIN DOUBLE, SHARESELLPRICE DOUBLE, SHAREOUT DOUBLE, PERSHARE DOUBLE,
            GOODSIN DOUBLE, GOODSOUT DOUBLE, GOODSSELLINGPRICE DOUBLE)
    """)
    con.execute("CREATE TABLE IF NOT EXISTS ALLDATE (DID INTEGER, ENGDATE DATE, WORKINGDAY VARCHAR, YEAREND VARCHAR, SALARYDAY VARCHAR)")
    con.execute("CREATE TABLE IF NOT EXISTS SHARELASTPRICED (SHARELASTPRICE DOUBLE)")
    
    # Only insert 0 if the table is empty
    count = con.execute("SELECT COUNT(*) FROM SHARELASTPRICED").fetchone()[0]
    if count == 0:
        con.execute("INSERT INTO SHARELASTPRICED VALUES (0)")

def populate_all_date(start_date=datetime(2023, 1, 1), num_days=365):
    # Check if already populated
    count = con.execute("SELECT COUNT(*) FROM ALLDATE").fetchone()[0]
    if count >= num_days:
        return

    for did in range(1, num_days + 1):
        dt = start_date + timedelta(days=did - 1)
        wd = 'Y' if dt.weekday() < 5 else 'N'
        ye = 'Y' if did == num_days else 'N'
        sd = 'Y' if dt.day == 1 else 'N'
        con.execute("INSERT INTO ALLDATE VALUES (?, ?, ?, ?, ?)", (did, dt, wd, ye, sd))