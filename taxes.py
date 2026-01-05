from db_init import con
from transactions import t_making
from shares import get_ctz_public_company, get_ctz_nbroker, get_ctz_government
from config import get_setup_val, corp_tax

def get_broker_corporate_tax_amt():
    bal = con.execute(f"SELECT SUM(CASHIN - CASHOUT) FROM TRANSACTIONS WHERE CITIZENSHIPNO = {get_ctz_nbroker()}").fetchone()[0] or 0
    prof = bal - get_setup_val('CapitalOfBrokerCompany')
    return round(prof * corp_tax(), 2) if prof > 0 else 0

def get_public_company_tax_amt():
    prof = con.execute(f"SELECT SUM(CASHIN - CASHOUT) FROM TRANSACTIONS WHERE CITIZENSHIPNO = {get_ctz_public_company()}").fetchone()[0] or 0
    return round(prof * corp_tax(), 2) if prof > 0 else 0

def make_corporate_tax_all():
    com, bro, gov = get_ctz_public_company(), get_ctz_nbroker(), get_ctz_government()
    b_tax = get_broker_corporate_tax_amt()
    p_tax = get_public_company_tax_amt()
    dt = con.execute("SELECT MAX(ENGDATE) FROM ALLDATE").fetchone()[0]
    det = f"Corporate Tax to Gov CTZ {gov}"

    t_making(dt, bro, det, 0, b_tax)
    t_making(dt, gov, f"Corp Tax from {bro}", b_tax, 0)
    t_making(dt, com, det, 0, p_tax)
    t_making(dt, gov, f"Corp Tax from {com}", p_tax, 0)