from db_init import con

def t_making(tdate, ctz, tdetail, chin=0, chot=0, shbypr=0, shin=0, shslpr=0, shot=0, parval=0, gdin=0, gdot=0, gdslpr=0):
    # Filter out transactions where all numerical values are zero
    numerical_values = (chin, chot, shbypr, shin, shslpr, shot, parval, gdin, gdot, gdslpr)
    if not any(v != 0 for v in numerical_values):
        return

    con.execute(
        "INSERT INTO TRANSACTIONS VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            tdate, ctz, tdetail, 
            round(chin, 2), round(chot, 2), round(shbypr, 2), round(shin, 2), 
            round(shslpr, 2), round(shot, 2), round(parval, 2), round(gdin, 2), 
            round(gdot, 2), round(gdslpr, 2)
        )
    )

def make_opening_cash():
    from shares import get_any_date, get_total_people
    from config import get_setup_val
    dt = get_any_date(1)
    ppl = get_total_people()
    ech = get_setup_val('CashWithEach')
    
    # Citizens
    for ctz in range(1, ppl + 1):
        t_making(dt, ctz, "Initial Cash Injection", chin=ech)
    
    # Companies starting capital
    from shares import get_ctz_nbroker, get_ctz_public_company
    bro = get_ctz_nbroker()
    com = get_ctz_public_company()
    
    t_making(dt, bro, "Initial Broker Capital", chin=get_setup_val('CapitalOfBrokerCompany'))
    # Public company capital is handled via share issuance in share_transaction_first, 
    # but we can record the 'CashWithEach' if they were treated as citizens too (they aren't in this simulation usually)