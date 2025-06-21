
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

st.title("Supermarket Cash Holding Tracker")
st.markdown("Enter daily cash holding and reconciliation details per store")

# Google Sheets connection
conn = st.experimental_connection("gsheets", type=GSheetsConnection)
existing_data = conn.read(worksheet="CashHoldings", ttl=5)
existing_data = existing_data.dropna(how="all")

# --- DROPDOWN FIELDS WITH COMMENTS ---
dropdown_fields = ["mpesa", "vooma", "pdq", "WHT", "Deposits", "Cashier_Variances"]

st.subheader("Cash Channel Exceptions")
selected_fields = st.multiselect("Select exceptions (if any):", dropdown_fields)

comments = {}
for field in selected_fields:
    comments[field] = st.text_area(f"Comment for {field} exception")

# --- MAIN FORM ---
with st.form(key="cash_form"):
    st.subheader("Cash Holding Details")

    store_id = st.text_input("Store ID")
    branch = st.text_input("Branch Name")
    record_date = st.date_input("Date", value=date.today())
    expected_cash = st.number_input("Expected Cash", min_value=0.0)

    cash_sales = st.number_input("Cash Sales", min_value=0.0)
    variance_sale = st.number_input("Variance Sale", min_value=0.0)
    opening_bal = st.number_input("Opening Balance", min_value=0.0)
    banking = st.number_input("Banking", min_value=0.0)
    petty_cash = st.number_input("Petty Cash", min_value=0.0)
    operating_float = st.number_input("Operating Float", min_value=0.0)

    additional_notes = st.text_area("General Notes")

    submit_button = st.form_submit_button("Submit Cash Record")

    if submit_button:
        if not store_id or not branch:
            st.warning("Store ID and Branch are required.")
            st.stop()

        if ((existing_data["store_id"] == store_id) & 
            (existing_data["date"] == record_date.strftime("%Y-%m-%d"))).any():
            st.warning("Entry already exists for this store and date.")
            st.stop()

        # Create comment string
        comment_string = "; ".join([f"{k}: {v}" for k, v in comments.items() if v])

        # Compose new row
        new_row = pd.DataFrame([{
            "store_id": store_id,
            "branch": branch,
            "date": record_date.strftime("%Y-%m-%d"),
            "expected_cash": expected_cash,
            "cash_sales": cash_sales,
            "variance_sale": variance_sale,
            "opening_bal": opening_bal,
            "banking": banking,
            "petty_cash": petty_cash,
            "operating_float": operating_float,
            "exceptions": ", ".join(selected_fields),
            "exception_comments": comment_string,
            "additional_notes": additional_notes
        }])

        updated_df = pd.concat([existing_data, new_row], ignore_index=True)
        conn.update(worksheet="CashHoldings", data=updated_df)

        st.success("Cash holding details successfully submitted!")
