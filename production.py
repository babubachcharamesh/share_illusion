import pandas as pd
import math
from db_init import con
from transactions import t_making
from shares import get_ctz_public_company, get_total_people
from config import get_setup_val, corp_tax

def make_daily_production():
    com = get_ctz_public_company()
    prod = get_setup_val('PerDayProduction')
    det = "Normal Daily Production"
    df = con.execute("SELECT ENGDATE, WORKINGDAY FROM ALLDATE").df()
    for _, r in df.iterrows():
        if r['WORKINGDAY'] == "Y":
            t_making(r['ENGDATE'], com, det, gdot=prod)

def product_allocate():
    wd = get_setup_val('WorkingDays', int)
    pd = get_setup_val('PerDayProduction')
    ppl = get_total_people()
    return round(wd * pd / ppl, 2)

def get_selling_price_per_unit():
    emp = get_setup_val('PublicCompanyEmployees', int)
    sal = get_setup_val('PublicCompanyEmployeesSalary')
    mon = get_setup_val('PublicCompanyEmployeesSalaryMonths', int)
    wd = get_setup_val('WorkingDays', int)
    dly = get_setup_val('PerDayProduction')
    div = get_setup_val('DividendExpected')
    ctx = corp_tax()
    pv = get_setup_val('ParValueOfShare')
    nos = get_setup_val('PublicCompanyNoOfShares', int)
    ppl = get_total_people()
    alloc = product_allocate()
    a = ((emp * sal * mon) + ((pv * nos * div) / (1 - ctx))) / (ppl * alloc)
    return round(a, 2)

def make_daily_sales():
    prod = get_setup_val('PerDayProduction')
    price = get_selling_price_per_unit()
    to_sale = product_allocate()
    com = get_ctz_public_company()
    val = round(price * to_sale, 2)
    ppl = get_total_people()
    tot_prod = prod * get_setup_val('WorkingDays', int)
    cur_prod = sold = 0
    ctz = 1

    df = con.execute("SELECT ENGDATE, WORKINGDAY FROM ALLDATE").df()
    for _, r in df.iterrows():
        if r['WORKINGDAY'] == "Y":
            cur_prod += prod
            while to_sale <= cur_prod and ctz <= ppl and sold < tot_prod:
                t_making(r['ENGDATE'], com, f"{to_sale:.2f} units sold to {ctz} @ {price:.2f}", val, 0, gdot=to_sale)
                t_making(r['ENGDATE'], ctz, f"{to_sale:.2f} units bought from PUBLIC COMPANY @ {price:.2f}", 0, val, gdin=to_sale)
                sold += to_sale
                ctz += 1
                cur_prod -= to_sale