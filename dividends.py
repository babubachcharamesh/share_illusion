import pandas as pd
from db_init import con
from transactions import t_making
from shares import get_ctz_public_company, get_ctz_government
from config import get_config, get_setup_val, parval, div_rate

def get_div_tax_rate():
    return get_setup_val('DividendTaxRate') if 'DividendTaxRate' in get_config() else 0.05

def get_last_date():
    return con.execute("SELECT MAX(ENGDATE) FROM ALLDATE").fetchone()[0]

def pub_com_dividend_payout():
    pv = parval()
    dt = get_last_date()
    dr = div_rate()
    dtax = get_div_tax_rate()
    com, gov = get_ctz_public_company(), get_ctz_government()

    con.execute("""
        CREATE OR REPLACE VIEW SHAREHOLDERSNETTING AS
        SELECT CITIZENSHIPNO, 'PUBLIC LIMITED' AS COMPANYNAME,
               SUM(SHAREIN - SHAREOUT) AS SHARES
        FROM TRANSACTIONS GROUP BY CITIZENSHIPNO
    """)

    df = con.execute("SELECT * FROM SHAREHOLDERSNETTING").df()
    for _, r in df.iterrows():
        ctz, shr = r['CITIZENSHIPNO'], r['SHARES']
        gross_amt = round(shr * pv * dr, 2)
        tx_amt = round(gross_amt * dtax, 2)
        net_amt = round(gross_amt - tx_amt, 2)

        t_making(dt, com, f"Div @ {dr*100:.2f}% to {ctz}", 0, gross_amt)
        t_making(dt, gov, f"Div Tax @ {dtax*100:.2f}%", tx_amt, 0)
        t_making(dt, ctz, f"Net Div after {dtax*100:.2f}% tax", net_amt, 0)