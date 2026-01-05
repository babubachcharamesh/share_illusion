import pandas as pd
from db_init import con
from counters import counters
from transactions import t_making
from shares import get_ctz_government
from config import personal_tax, get_setup_val

get_gov_sal = lambda: get_setup_val('GovernmentEmployeesSalary')
get_bro_sal = lambda: get_setup_val('BrokerCompanyEmployeesSalary')
get_pub_sal = lambda: get_setup_val('PublicCompanyEmployeesSalary')

def get_next_salary_day(aday):
    res = con.execute("SELECT ENGDATE, DID FROM ALLDATE WHERE SALARYDAY = 'Y' AND DID > ? ORDER BY DID LIMIT 1", (aday,)).fetchone()
    if res:
        counters.SALARYDAY = res[1]
        return res[0]
    return None

def salary_making(emp_ctz, emp_employer_ctz, emplyr, sal):
    gov = get_ctz_government()
    tax = personal_tax()
    df = con.execute("SELECT ENGDATE FROM ALLDATE WHERE SALARYDAY = 'Y'").df()
    for _, r in df.iterrows():
        dt = r['ENGDATE']
        tax_amt = round(sal * tax, 2)
        net = round(sal - tax_amt, 2)
        t_making(dt, emp_ctz, f"Salary from {emplyr}", net, 0)
        t_making(dt, emp_employer_ctz, f"Salary to {emp_ctz}", 0, sal)
        t_making(dt, gov, f"Tax from {emp_ctz}", tax_amt, 0)

def salary_to_make():
    df = con.execute("SELECT CITIZENSHIPNO, EMPLOYER, EMPLOYERCTZN FROM ALLPEOPLE WHERE EMPLOYER IS NOT NULL").df()
    for _, r in df.iterrows():
        ctz, emp, ectz = r['CITIZENSHIPNO'], r['EMPLOYER'], r['EMPLOYERCTZN']
        sal = get_gov_sal() if emp == "GOVERNMENT" else (get_bro_sal() if emp == "BROKER COMPANY" else get_pub_sal())
        salary_making(ctz, ectz, emp, sal)