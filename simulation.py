# simulation.py (top of file)

from contextlib import contextmanager
from db_init import con
from config import get_setup_val, parval
from counters import counters

# Import everything we use from shares
from shares import (
    make_people_cash,
    add_shares,
    share_transaction_first,
    share_transactioning,
    get_total_people
)

# Other modules
from employment import making_employment
from salary import salary_to_make
from production import make_daily_production, make_daily_sales
from taxes import make_corporate_tax_all
from dividends import pub_com_dividend_payout
from transactions import make_opening_cash

@contextmanager
def sim_transaction():
    yield

def make_all_thing():
    counters.reset()
    con.execute("DELETE FROM ALLPEOPLE")
    con.execute("DELETE FROM SHARELIST")
    con.execute("DELETE FROM TRANSACTIONS")

    with sim_transaction():
        bc_start = 1
        bc_pro = get_setup_val('PromotorsOfBrokerCompany', int)
        bc_cap = round(get_setup_val('CapitalOfBrokerCompany') / bc_pro, 2)

        pub_pro_start = bc_start + bc_pro
        pub_pro = get_setup_val('PromotorsOfPublicCompany', int)

        pv = parval()
        nos = get_setup_val('PublicCompanyNoOfShares', int)
        pub_hold = get_setup_val('PublicHolding')
        pub_pro_total = pv * nos * (1 - pub_hold)
        pub_pro_cap = round(pub_pro_total / pub_pro, 2)

        pub_gen_start = pub_pro_start + pub_pro
        pub_gen = get_setup_val('PublicCompanyPublicShareholders', int)
        pub_gen_total = pv * nos * pub_hold
        pub_gen_cap = round(pub_gen_total / pub_gen, 2)

        make_people_cash(get_total_people(), get_setup_val('CashWithEach'))
        add_shares(bc_start, "BROKER PVT LTD", bc_pro, bc_cap, 'PROMOTORSHARE')
        add_shares(pub_pro_start, "PUBLIC LIMITED", pub_pro, pub_pro_cap, 'PROMOTORSHARE')
        add_shares(pub_gen_start, "PUBLIC LIMITED", pub_gen, pub_gen_cap, 'PUBLICSHARE')

        make_opening_cash()
        share_transaction_first()
        share_transactioning()

        making_employment()
        salary_to_make()
        make_daily_production()
        make_daily_sales()
        make_corporate_tax_all()
        pub_com_dividend_payout()