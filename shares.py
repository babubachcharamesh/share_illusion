import pandas as pd
import streamlit as st
from db_init import con
from counters import counters
from transactions import t_making
from config import parval, brokerage, cap_gain, daily_profit, get_setup_val

def get_total_people():
    return int(get_setup_val('TotalPeople', int))

def get_cash_each():
    return get_setup_val('CashWithEach')

def make_people_cash(ppl, ech):
    for cnt in range(1, ppl + 4):
        con.execute("INSERT INTO ALLPEOPLE (CITIZENSHIPNO, CASHBALANCE) VALUES (?, ?)", (cnt, 0 if cnt > ppl else ech))

def add_shares(start_ctz, company, count, value, col='PROMOTORSHARE'):
    ct = start_ctz - 1
    v = round(value, 2)
    for _ in range(count):
        ct += 1
        con.execute(f"INSERT INTO SHARELIST (CITIZENSHIPNO, COMPANYNAME, {col}) VALUES (?, ?, ?)", (ct, company, v))

def get_any_date(ddd):
    res = con.execute("SELECT ENGDATE FROM ALLDATE WHERE DID = ?", (ddd,)).fetchone()
    return res[0] if res else None

def share_transaction_first():
    pv = parval()
    dt = get_any_date(2)
    pub_ctz = get_ctz_public_company()
    bro_ctz = get_ctz_nbroker()

    df = con.execute("SELECT * FROM SHARELIST").df()
    for _, r in df.iterrows():
        ctzn, cnam = r['CITIZENSHIPNO'], r['COMPANYNAME']
        prsh = r.get('PROMOTORSHARE', 0)
        pbsh = r.get('PUBLICSHARE', 0)
        comp_ctz = bro_ctz if cnam == "BROKER PVT LTD" else pub_ctz

        if prsh > 0:
            cash = prsh
            nos = round(prsh / pv, 2)
            td = f"{nos:.2f} kitta Promotor Shares of {cnam} bought @ {pv:.2f}"
            cd = f"{nos:.2f} kitta Promotor Shares sold to {ctzn} @ {pv:.2f}"
        else:
            cash = pbsh
            nos = round(pbsh / pv, 2)
            td = f"{nos:.2f} kitta Public Shares of {cnam} bought @ {pv:.2f}"
            cd = f"{nos:.2f} kitta Public Shares sold to {ctzn} @ {pv:.2f}"

        t_making(dt, ctzn, td, 0, cash, pv, nos, 0, 0, pv, 0, 0, 0)
        t_making(dt, comp_ctz, cd, cash, 0, 0, 0, pv, nos, pv, 0, 0, 0)

def get_ctz_nbroker():
    return con.execute("SELECT MAX(CITIZENSHIPNO) FROM ALLPEOPLE").fetchone()[0] or 0

get_ctz_public_company = lambda: get_ctz_nbroker() - 1
get_ctz_government = lambda: get_ctz_nbroker() - 2

def share_price_buy(ctzn):
    df = con.execute("SELECT SHAREBUYPRICE FROM TRANSACTIONS WHERE CITIZENSHIPNO = ? AND SHAREIN > 0 LIMIT 1", (ctzn,)).df()
    return df.iloc[0]['SHAREBUYPRICE'] if not df.empty else 0

def share_buy_no(ctzn):
    df = con.execute("SELECT SHAREIN FROM TRANSACTIONS WHERE CITIZENSHIPNO = ? AND SHAREIN > 0 LIMIT 1", (ctzn,)).df()
    return df.iloc[0]['SHAREIN'] if not df.empty else 0

def share_transaction_all(seller, buyer, price, day):
    pv = parval()
    sh_no = share_buy_no(seller)
    buy_val = round(price * sh_no * (1 + brokerage()), 2)
    sell_val = round((price * sh_no * (1 - brokerage())) - (sh_no * (price - pv) * cap_gain()), 2)
    cap_amt = round((price - pv) * sh_no * cap_gain(), 2)

    t_making(day, buyer, f"{sh_no:.2f} kitta Public Shares bought @ {price:.2f}", 0, buy_val, price, sh_no, 0, 0, pv, 0, 0, 0)
    t_making(day, seller, f"{sh_no:.2f} kitta Public Shares sold @ {price:.2f}", sell_val, 0, price, 0, 0, sh_no, pv, 0, 0, 0)

    comm = round(price * brokerage() * sh_no, 2)
    t_making(day, get_ctz_nbroker(), f"Brokerage @ {brokerage()*100:.2f}% sold {sh_no:.2f} kitta", comm, 0)
    t_making(day, get_ctz_nbroker(), f"Brokerage @ {brokerage()*100:.2f}% bought {sh_no:.2f} kitta", comm, 0)

    t_making(day, get_ctz_government(), f"Cap Gain Tax @ {cap_gain()*100:.2f}% on {sh_no:.2f} kitta", cap_amt, 0)

def make_last_price_of_share(slp):
    con.execute("UPDATE SHARELASTPRICED SET SHARELASTPRICE = ?", (slp,))

def get_next_working_day(aday):
    res = con.execute("SELECT ENGDATE, DID FROM ALLDATE WHERE WORKINGDAY = 'Y' AND DID > ? ORDER BY DID LIMIT 1", (aday,)).fetchone()
    if res:
        counters.WORKDAY = res[1]
        return res[0]
    return None

def share_transactioning():
    val = parval()
    dp = daily_profit()
    cnt = 0
    df = con.execute("SELECT * FROM SHARELIST").df()
    buyer_start = int(round(get_total_people() / 2, 0) + 1)
    lst_day = None

    tp = get_total_people()
    for _, r in df.iterrows():
        ctzn = r['CITIZENSHIPNO']
        pbsh = r.get('PUBLICSHARE', 0)
        if pbsh > 0:
            seller = ctzn
            # Ensure buyer index stays within [1, TotalPeople]
            buyer = buyer_start + cnt
            if buyer > tp:
                buyer = (buyer - 1) % tp + 1
            
            day = get_next_working_day(counters.WORKDAY)
            if day is None: break

            if lst_day is None or day > lst_day:
                val += dp

            share_transaction_all(seller, buyer, val, day)
            cnt += 1
            lst_day = day

    make_last_price_of_share(val)