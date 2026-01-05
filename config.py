from functools import lru_cache
from db_init import con

@lru_cache(maxsize=1)
def get_config():
    return con.execute("SELECT * FROM BASICSETUP").df().iloc[0].to_dict()

def get_setup_val(key, typ=float):
    return typ(get_config()[key])

parval    = lambda: get_setup_val('ParValueOfShare')
brokerage = lambda: get_setup_val('BrokerageRate')
cap_gain  = lambda: get_setup_val('CapitalGainTaxRate')
daily_profit = lambda: get_setup_val('ProfitMarginDaily')
daily_prod = lambda: get_setup_val('PerDayProduction')
div_rate  = lambda: get_setup_val('DividendExpected')
corp_tax  = lambda: get_setup_val('CorporateTaxRate')
personal_tax = lambda: get_setup_val('PersonalTaxRate')

def insert_sample_basic_setup():
    vals = {
        'TotalPeople': 500, 'CashWithEach': 650000.0, 'PromotorsOfBrokerCompany': 2, 'CapitalOfBrokerCompany': 1000000.0,
        'PromotorsOfPublicCompany': 25, 'ParValueOfShare': 100.0, 'PublicCompanyNoOfShares': 500000, 'PublicHolding': 0.6,
        'PublicCompanyPublicShareholders': 300, 'BrokerageRate': 0.0100, 'CapitalGainTaxRate': 0.1000, 'ProfitMarginDaily': 1.000,
        'GovernmentEmployees': 1, 'BrokerCompanyEmployees': 5, 'PublicCompanyEmployees': 67,
        'GovernmentEmployeesSalary': 40000.0, 'BrokerCompanyEmployeesSalary': 40000.0, 'PublicCompanyEmployeesSalary': 70000.0,
        'PersonalTaxRate': 0.1000, 'PerDayProduction': 4.0, 'DividendExpected': 0.0500, 'CorporateTaxRate': 0.2500,
        'WorkingDays': 250, 'PublicCompanyEmployeesSalaryMonths': 12, 'GeneralPublic':600
    }
    cols = ', '.join(vals)
    ph = ', '.join(['?'] * len(vals))
    con.execute(f"INSERT INTO BASICSETUP ({cols}) VALUES ({ph})", list(vals.values()))