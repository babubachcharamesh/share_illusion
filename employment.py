import pandas as pd
from db_init import con
from config import get_setup_val
from shares import get_ctz_government, get_ctz_nbroker, get_ctz_public_company

get_gov_emp = lambda: int(get_setup_val('GovernmentEmployees', int))
get_broker_emp = lambda: int(get_setup_val('BrokerCompanyEmployees', int))
get_pub_emp = lambda: int(get_setup_val('PublicCompanyEmployees', int))

def get_first_employee():
    return con.execute("SELECT MIN(CITIZENSHIPNO) FROM ALLPEOPLE WHERE EMPLOYER IS NOT NULL").fetchone()[0] or 0

def making_employment():
    gov = get_gov_emp()
    bro = get_broker_emp()
    pub = get_pub_emp()
    fst = get_first_employee()
    tot = gov + bro + pub
    cnt = 1

    df = con.execute("SELECT * FROM ALLPEOPLE ORDER BY CITIZENSHIPNO").df()
    for _, r in df.iterrows():
        ctz = r['CITIZENSHIPNO']
        if ctz >= fst and cnt <= tot:
            if cnt <= gov:
                emp = "GOVERNMENT"
                ectz = get_ctz_government()
            elif cnt <= gov + bro:
                emp = "BROKER COMPANY"
                ectz = get_ctz_nbroker()
            else:
                emp = "PUBLIC COMPANY"
                ectz = get_ctz_public_company()
            con.execute("UPDATE ALLPEOPLE SET EMPLOYER = ?, EMPLOYERCTZN = ? WHERE CITIZENSHIPNO = ?", (emp, ectz, ctz))
            cnt += 1