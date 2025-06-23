import streamlit as st
import pandas as pd
from datetime import date
from data import JOBS, COST_CODES, ENTRIES

st.title("Crew Tracker Prototype (Mock Data)")

# --- New Entry Form ---
with st.form("new_entry"):
    d = st.date_input("Date", date.today())
    job_id = st.selectbox(
        "Job", JOBS["id"],
        format_func=lambda x: JOBS.loc[JOBS.id == x, "name"].iloc[0]
    )
    cc_id = st.selectbox(
        "Cost Code", COST_CODES["id"],
        format_func=lambda x: COST_CODES.loc[COST_CODES.id == x, "code"].iloc[0]
    )
    hrs = st.number_input("Total Hours", min_value=0.0, step=0.5)
    units = st.number_input("Units Installed", min_value=0)
    if st.form_submit_button("Save Entry"):
        ENTRIES.loc[len(ENTRIES)] = {
            "date": d,
            "job_id": job_id,
            "cost_code_id": cc_id,
            "hours": hrs,
            "units_installed": units
        }
        ENTRIES.to_csv("entries.csv", index=False)
        st.success("Entry saved!")

# --- Edit Past Entries ---
edited_entries = st.data_editor(
    ENTRIES,
    use_container_width=True,
    # If you want to allow adding/deleting rows:
    allow_insert=True,
    allow_delete=True,
)

if st.button("Save All Edits"):
    edited_entries.to_csv("entries.csv", index=False)
    st.success("All edits saved!")
    ENTRIES = edited_entries.copy()

# --- Reporting ---
st.header("Performance Report")
sel = st.selectbox(
    "Select Job for Report", JOBS["id"],
    format_func=lambda x: JOBS.loc[JOBS.id == x, "name"].iloc[0]
)
df = ENTRIES[ENTRIES.job_id == sel].copy()
if not df.empty:
    # Join PMPH goals
    df = df.merge(
        COST_CODES[["id", "pmph_goal"]],
        left_on="cost_code_id", right_on="id"
    )
    df["estimated"] = df["hours"] * df["pmph_goal"]
    df["variance"]  = df["units_installed"] - df["estimated"]
    st.dataframe(
        df[["date", "cost_code_id", "hours", "units_installed", "estimated", "variance"]]
    )
    st.line_chart(
        df.set_index("date")[["units_installed", "estimated", "variance"]]
    )
else:
    st.info("No entries for this job yet.")
