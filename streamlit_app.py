import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# App Title
st.title("Daily Cash Holdings Entry")
st.markdown("Submit daily branch cash and mobile money details below.")

# Connect to Google Sheets
conn = st.experimental_connection("gsheets", type=GSheetsConnection)

# Fetch existing sheet data for dropdowns (assuming separate sheets/tabs hold reference values)
mpesa_options = conn.read(worksheet="mpesa_options")["value"].dropna().tolist()
vooma_options = conn.read(worksheet="vooma_options")["value"].dropna().tolist()
pdq_options = conn.read(worksheet="pdq_options")["value"].dropna().tolist()
wht_options = conn.read(worksheet="wht_options")["value"].dropna().tolist()
deposit_options = conn.read(worksheet="deposit_options")["value"].dropna().tolist()

# Existing data
existing_data = conn.read(worksheet="Cash_Entries", ttl=5)
existing_data = existing_data.dropna(how="all")

# Cash Holding Form
with st.form("cash_form"):
    st.subheader("Branch & Date Information")
    store_id = st.text_input("Store ID (as per email)*")
    branch = st.text_input("Branch Name*")
    date = st.date_input("Date", value=datetime.date.today())

    st.subheader("Cash & Mobile Money Inputs")
    mpesa = st.multiselect("Mpesa*", options=mpesa_options)
    vooma = st.multiselect("Vooma*", options=vooma_options)
    pdq = st.multiselect("PDQ*", options=pdq_options)
    wht = st.multiselect("WHT*", options=wht_options)
    deposits = st.multiselect("Deposits*", options=deposit_options)

    till_closure = st.number_input("Till Closure", step=1.0)
    manual_adj = st.number_input("Manual Adjustments", step=1.0)
    cash_sales = st.number_input("Cash Sales", step=1.0)
    petty_cash = st.number_input("Petty Cash", step=1.0)

    st.subheader("Cash Breakdown & Variance Entries")
    part_one = st.number_input("Part One", step=1.0)
    last_card = st.number_input("Last Card", step=1.0)
    lose = st.number_input("Lose", step=1.0)
    agency = st.number_input("Agency", step=1.0)
    change_account = st.number_input("Change Account", step=1.0)
    mpesa_float = st.number_input("Mpesa Float", step=1.0)
    interbranch = st.number_input("Interbranch", step=1.0)
    pcv = st.number_input("PCV", step=1.0)
    coins = st.number_input("Coins", step=1.0)
    cashiers_change = st.number_input("Cashiers Change", step=1.0)
    total_breakdown = st.number_input("Total Breakdown", step=1.0)
    operating_float = st.number_input("Operating Float", step=1.0)

    st.subheader("End of Day Balances")
    mpesa_amt = st.number_input("Mpesa Amount", step=1.0)
    cash_amt = st.number_input("Cash Amount", step=1.0)
    equity_coop = st.number_input("Equity Coop", step=1.0)
    chief_cashier = st.number_input("Chief Cashier", step=1.0)
    agency_variance = st.number_input("Agency Variance", step=1.0)
    change_op_bal = st.number_input("Change Opening Bal", step=1.0)
    change_added = st.number_input("Change Added", step=1.0)
    change_banking = st.number_input("Change Banking", step=1.0)
    change_bal = st.number_input("Change Bal", step=1.0)
    floats_op_bal = st.number_input("Floats Opening Bal", step=1.0)
    floats_added = st.number_input("Floats Added", step=1.0)
    floats_banking = st.number_input("Floats Banking", step=1.0)
    balance = st.number_input("Balance", step=1.0)

    submitted = st.form_submit_button("Submit Entry")

    if submitted:
        if not store_id or not branch:
            st.warning("Store ID and Branch are mandatory.")
            st.stop()

        new_data = pd.DataFrame([{
            "store_id": store_id,
            "branch": branch,
            "date": date.strftime("%Y-%m-%d"),
            "mpesa": ", ".join(mpesa),
            "vooma": ", ".join(vooma),
            "pdq": ", ".join(pdq),
            "wht": ", ".join(wht),
            "deposits": ", ".join(deposits),
            "till_closure": till_closure,
            "manual_adj": manual_adj,
            "cash_sales": cash_sales,
            "petty_cash": petty_cash,
            "part_one": part_one,
            "last_card": last_card,
            "lose": lose,
            "agency": agency,
            "change_account": change_account,
            "mpesa_float": mpesa_float,
            "interbranch": interbranch,
            "pcv": pcv,
            "coins": coins,
            "cashiers_change": cashiers_change,
            "total_breakdown": total_breakdown,
            "operating_float": operating_float,
            "mpesa_amt": mpesa_amt,
            "cash_amt": cash_amt,
            "equity_coop": equity_coop,
            "chief_cashier": chief_cashier,
            "agency_variance": agency_variance,
            "change_op_bal": change_op_bal,
            "change_added": change_added,
            "change_banking": change_banking,
            "change_bal": change_bal,
            "floats_op_bal": floats_op_bal,
            "floats_added": floats_added,
            "floats_banking": floats_banking,
            "balance": balance,
        }])

        # Append new data and update sheet
        updated_df = pd.concat([existing_data, new_data], ignore_index=True)
        conn.update(worksheet="Cash_Entries", data=updated_df)
        st.success("Cash entry submitted successfully!")
