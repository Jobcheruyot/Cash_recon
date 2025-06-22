import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# App title
st.title("Branch Cash Entry Management")

# Establish Google Sheets connection
conn = st.experimental_connection("gsheets", type=GSheetsConnection)

# Fetch dropdown options
def get_options(sheet_name):
    return conn.read(worksheet=sheet_name)["value"].dropna().tolist()

mpesa_options = get_options("mpesa_options")
vooma_options = get_options("vooma_options")
pdq_options = get_options("pdq_options")
wht_options = get_options("wht_options")
deposit_options = get_options("deposit_options")

# Fetch existing data
existing_data = conn.read(worksheet="Cash_Entries", ttl=5)
existing_data = existing_data.dropna(how="all")

# Select action
action = st.selectbox(
    "Choose an Action",
    ["New Cash Entry", "Update Existing Entry", "View All Entries", "Delete Entry"]
)

# Shared fields function
def cash_form_fields(data=None):
    with st.form("cash_form"):
        store_id = st.text_input("Store ID*", value=data.get("store_id", "") if data else "")
        branch = st.text_input("Branch*", value=data.get("branch", "") if data else "")
        date = st.date_input("Date*", value=pd.to_datetime(data["date"]) if data else datetime.date.today())
        mpesa = st.multiselect("Mpesa*", mpesa_options, default=data.get("mpesa", "").split(", ") if data else [])
        vooma = st.multiselect("Vooma*", vooma_options, default=data.get("vooma", "").split(", ") if data else [])
        pdq = st.multiselect("PDQ*", pdq_options, default=data.get("pdq", "").split(", ") if data else [])
        till_closure = st.number_input("Till Closure", step=1.0, value=float(data.get("till_closure", 0)) if data else 0)
        manual_adj = st.number_input("Manual Adj", step=1.0, value=float(data.get("manual_adj", 0)) if data else 0)
        cash_sales = st.number_input("Cash Sales", step=1.0, value=float(data.get("cash_sales", 0)) if data else 0)
        petty_cash = st.number_input("Petty Cash", step=1.0, value=float(data.get("petty_cash", 0)) if data else 0)

        submit = st.form_submit_button("Submit")
        return {
            "submit": submit,
            "store_id": store_id,
            "branch": branch,
            "date": date,
            "mpesa": ", ".join(mpesa),
            "vooma": ", ".join(vooma),
            "pdq": ", ".join(pdq),
            "till_closure": till_closure,
            "manual_adj": manual_adj,
            "cash_sales": cash_sales,
            "petty_cash": petty_cash
        }

# ADD NEW ENTRY
if action == "New Cash Entry":
    st.subheader("Submit New Cash Entry")
    result = cash_form_fields()

    if result["submit"]:
        if not result["store_id"] or not result["branch"]:
            st.warning("Store ID and Branch are required.")
        else:
            new_entry = pd.DataFrame([result])
            updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
            conn.update(worksheet="Cash_Entries", data=updated_df)
            st.success("Cash entry submitted.")

# UPDATE EXISTING ENTRY
elif action == "Update Existing Entry":
    st.subheader("Update Entry")
    entry_options = existing_data["store_id"] + " - " + existing_data["date"]
    selected = st.selectbox("Select an entry", options=entry_options)

    selected_data = existing_data[entry_options == selected].iloc[0].to_dict()
    result = cash_form_fields(selected_data)

    if result["submit"]:
        # Remove old and add updated entry
        existing_data = existing_data.drop(
            existing_data[entry_options == selected].index
        )
        updated_df = pd.concat([existing_data, pd.DataFrame([result])], ignore_index=True)
        conn.update(worksheet="Cash_Entries", data=updated_df)
        st.success("Entry updated successfully.")

# VIEW ENTRIES
elif action == "View All Entries":
    st.subheader("All Branch Entries")
    st.dataframe(existing_data)

# DELETE ENTRY
elif action == "Delete Entry":
    st.subheader("Delete Entry")
    entry_options = existing_data["store_id"] + " - " + existing_data["date"]
    selected = st.selectbox("Select an entry to delete", options=entry_options)

    if st.button("Delete"):
        existing_data = existing_data.drop(existing_data[entry_options == selected].index)
        conn.update(worksheet="Cash_Entries", data=existing_data)
        st.success("Entry deleted.")
