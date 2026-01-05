# app.py
import streamlit as st
import pandas as pd
from db_init import con, initialize_tables, populate_all_date
from config import insert_sample_basic_setup
from simulation import make_all_thing

# Page configuration
st.set_page_config(page_title="Economic Simulation", layout="wide")

st.title("Economic Simulation - Configuration & Run")

st.markdown("""
**Instructions**  
1. Edit the values in the sections below  
2. **TotalPeople** is automatically calculated and cannot be changed directly  
3. Click **Save Configuration Changes**  
4. Then click **Run Simulation**
""")

# Initialize database + calendar only once
if 'db_initialized' not in st.session_state:
    initialize_tables()
    populate_all_date()
    st.session_state.db_initialized = True

# Check if BASICSETUP has data
setup_count = con.execute("SELECT COUNT(*) FROM BASICSETUP").fetchone()[0]

# Auto-insert default values if table is empty
if setup_count == 0:
    with st.spinner("Inserting default configuration..."):
        insert_sample_basic_setup()
    st.success("Default configuration loaded automatically.")
    st.session_state.config_saved = True

# ──────────────────────────────────────────────────────────────
# Load current BASICSETUP (single row)
df_setup_raw = con.execute("SELECT * FROM BASICSETUP").df()
if df_setup_raw.empty:
    st.warning("Configuration is empty. Please save or reload default configuration.")
    st.stop()
df_setup = df_setup_raw.iloc[0]

# ──────────────────────────────────────────────────────────────
# Helper function to calculate TotalPeople
def calculate_total_people(gov, prom_bro, bro_emp, prom_pub, pub_sh, pub_emp, gen_pub):
    return (
        prom_bro +
        prom_pub +
        pub_sh +
        gov +
        bro_emp +
        pub_emp +
        gen_pub
    )

# ──────────────────────────────────────────────────────────────
# Display editable fields in groups (single column layout)
st.subheader("Configuration Settings")

with st.container():
    col1 = st.columns(1)[0]
    with col1:
        st.markdown("### People & Population")

        # Editable fields that contribute to TotalPeople

        gov_employees = st.number_input(
            "GovernmentEmployees",
            min_value=0,
            value=int(df_setup['GovernmentEmployees']),
            step=1,
            key="gov_emp"
        )

        promotors_broker = st.number_input(
            "PromotorsOfBrokerCompany",
            min_value=0,
            value=int(df_setup['PromotorsOfBrokerCompany']),
            step=1,
            key="prom_broker"
        )

        broker_employees = st.number_input(
            "BrokerCompanyEmployees",
            min_value=0,
            value=int(df_setup['BrokerCompanyEmployees']),
            step=1,
            key="broker_emp"
        )

        promotors_pub = st.number_input(
            "PromotorsOfPublicCompany",
            min_value=0,
            value=int(df_setup['PromotorsOfPublicCompany']),
            step=1,
            key="prom_pub"
        )

        pub_shareholders = st.number_input(
            "PublicCompanyPublicShareholders",
            min_value=0,
            value=int(df_setup['PublicCompanyPublicShareholders']),
            step=1,
            key="pub_shareholders"
        )

        pub_employees = st.number_input(
            "PublicCompanyEmployees",
            min_value=0,
            value=int(df_setup['PublicCompanyEmployees']),
            step=1,
            key="pub_emp"
        )

        pub_general = st.number_input(
            "GeneralPublic",
            min_value=0,
            value=int(df_setup['GeneralPublic']),
            step=1,
            key="pub_gen"
        )

        # Display read-only TotalPeople
        total_people = calculate_total_people(
            gov_employees, promotors_broker, broker_employees,
            promotors_pub, pub_shareholders, pub_employees, pub_general
        )
        st.metric("TotalPeople (calculated)", total_people)

        st.markdown("---")

        st.markdown("### Financial & Share Parameters")
        cash_each = st.number_input(
            "CashWithEach",
            min_value=0.0,
            value=float(df_setup['CashWithEach']),
            step=100.0,
            format="%.2f",
            key="cash_each"
        )

        capital_broker = st.number_input(
            "CapitalOfBrokerCompany",
            min_value=0.0,
            value=float(df_setup['CapitalOfBrokerCompany']),
            step=10000.0,
            format="%.2f",
            key="cap_broker"
        )

        par_value = st.number_input(
            "ParValueOfShare",
            min_value=0.0,
            value=float(df_setup['ParValueOfShare']),
            step=1.0,
            format="%.2f",
            key="par_value"
        )

        pub_shares = st.number_input(
            "PublicCompanyNoOfShares",
            min_value=0,
            value=int(df_setup['PublicCompanyNoOfShares']),
            step=100,
            key="pub_shares"
        )

        pub_holding = st.number_input(
            "PublicHolding",
            min_value=0.0,
            max_value=1.0,
            value=float(df_setup['PublicHolding']),
            step=0.01,
            format="%.4f",
            key="pub_holding"
        )

        st.markdown("---")

        st.markdown("### Rates & Economic Parameters")
        brokerage_rate = st.number_input(
            "BrokerageRate",
            min_value=0.0,
            max_value=1.0,
            value=float(df_setup['BrokerageRate']),
            step=0.001,
            format="%.4f",
            key="brokerage_rate"
        )

        cap_gain_tax = st.number_input(
            "CapitalGainTaxRate",
            min_value=0.0,
            max_value=1.0,
            value=float(df_setup['CapitalGainTaxRate']),
            step=0.001,
            format="%.4f",
            key="cap_gain_tax"
        )

        profit_margin = st.number_input(
            "ProfitMarginDaily",
            min_value=0.0,
            value=float(df_setup['ProfitMarginDaily']),
            step=0.001,
            format="%.4f",
            key="profit_margin"
        )

        personal_tax = st.number_input(
            "PersonalTaxRate",
            min_value=0.0,
            max_value=1.0,
            value=float(df_setup['PersonalTaxRate']),
            step=0.01,
            format="%.4f",
            key="personal_tax"
        )

        corp_tax_rate = st.number_input(
            "CorporateTaxRate",
            min_value=0.0,
            max_value=1.0,
            value=float(df_setup['CorporateTaxRate']),
            step=0.01,
            format="%.4f",
            key="corp_tax_rate"
        )

        dividend_exp = st.number_input(
            "DividendExpected",
            min_value=0.0,
            max_value=1.0,
            value=float(df_setup['DividendExpected']),
            step=0.01,
            format="%.4f",
            key="dividend_exp"
        )

        daily_prod = st.number_input(
            "PerDayProduction",
            min_value=0.0,
            value=float(df_setup['PerDayProduction']),
            step=100.0,
            key="daily_prod"
        )

# ──────────────────────────────────────────────────────────────
# Save button
if st.button("💾 Save Configuration Changes", type="primary"):
    # Prepare new values (using current input values)
    new_values = {
        'GeneralPublic': pub_general,
        'TotalPeople': calculate_total_people(
            gov_employees, promotors_broker, broker_employees,
            promotors_pub, pub_shareholders, pub_employees, pub_general
        ),
        'CashWithEach': cash_each,
        'PromotorsOfBrokerCompany': promotors_broker,
        'CapitalOfBrokerCompany': capital_broker,
        'PromotorsOfPublicCompany': promotors_pub,
        'ParValueOfShare': par_value,
        'PublicCompanyNoOfShares': pub_shares,
        'PublicHolding': pub_holding,
        'PublicCompanyPublicShareholders': pub_shareholders,
        'BrokerageRate': brokerage_rate,
        'CapitalGainTaxRate': cap_gain_tax,
        'ProfitMarginDaily': profit_margin,
        'GovernmentEmployees': gov_employees,
        'BrokerCompanyEmployees': broker_employees,
        'PublicCompanyEmployees': pub_employees,
        'GovernmentEmployeesSalary': df_setup['GovernmentEmployeesSalary'],
        'BrokerCompanyEmployeesSalary': df_setup['BrokerCompanyEmployeesSalary'],
        'PublicCompanyEmployeesSalary': df_setup['PublicCompanyEmployeesSalary'],
        'PersonalTaxRate': personal_tax,
        'PerDayProduction': daily_prod,
        'DividendExpected': dividend_exp,
        'CorporateTaxRate': corp_tax_rate,
        'WorkingDays': df_setup['WorkingDays'],
        'PublicCompanyEmployeesSalaryMonths': df_setup['PublicCompanyEmployeesSalaryMonths']
    }

    # Delete old row
    con.execute("DELETE FROM BASICSETUP")

    # Insert new row
    columns = ', '.join(new_values.keys())
    placeholders = ', '.join(['?'] * len(new_values))
    con.execute(f"INSERT INTO BASICSETUP ({columns}) VALUES ({placeholders})", list(new_values.values()))

    st.success("✅ Configuration saved successfully!")
    from config import get_config
    get_config.cache_clear()
    st.session_state.config_saved = True
    st.rerun()

# ──────────────────────────────────────────────────────────────
# Run Simulation
st.markdown("---")

if st.session_state.get('config_saved', setup_count > 0):
    if st.button("🚀 Run Simulation", type="primary"):
        with st.spinner("Running full economic simulation..."):
            make_all_thing()
        st.success("Simulation completed successfully!")

        with st.expander("Transactions Table"):
            st.dataframe(con.execute("SELECT * FROM TRANSACTIONS").df())

        with st.expander("Citizens (All People)"):
            st.dataframe(con.execute("SELECT * FROM ALLPEOPLE").df())

        with st.expander("Share Ownership"):
            st.dataframe(con.execute("SELECT * FROM SHARELIST").df())
else:
    st.info("Please save the configuration first.")

# ──────────────────────────────────────────────────────────────
# SQL Explorer
st.markdown("---")
st.header("🔍 SQL Explorer")
st.markdown("Run custom SELECT queries on the simulation database.")

# Sample query as default
default_query = "SELECT * FROM TRANSACTIONS LIMIT 10"
user_query = st.text_area("Enter your SQL SELECT query here:", value=default_query, height=150)

if st.button("▶️ Execute Query"):
    if user_query.strip().upper().startswith("SELECT"):
        try:
            # Execute query and convert to DataFrame
            res_df = con.execute(user_query).df()
            
            if not res_df.empty:
                st.subheader("Query Results")
                st.dataframe(res_df, use_container_width=True)
                
                # Conversion for download
                csv = res_df.to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label="📥 Download results as CSV",
                    data=csv,
                    file_name="query_results.csv",
                    mime="text/csv",
                )
            else:
                st.info("Query returned no results.")
        except Exception as e:
            st.error(f"❌ Error executing query: {e}")
    else:
        st.warning("⚠️ Only SELECT queries are allowed in this explorer.")
