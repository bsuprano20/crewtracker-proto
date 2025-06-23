import streamlit as st
import pandas as pd
from datetime import date
from data import JOBS, COST_CODES, ENTRIES

# --- Simple Authentication ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Please Log In")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "bsuprano" and password == "password":
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Invalid credentials. Please try again.")
    st.stop()

# --- Main App ---
st.title("Crew Tracker Prototype (Mock Data)")

# --- New Entry Form ---
with st.form("new_entry"):
    d = st.date_input("Date", date.today())
    job_id = st.selectbox(
        "Job", JOBS["id"],
        format_func=lambda x: JOBS.loc[JOBS.id == x, "name"].iloc[0]
    )
    cc_id = st.selectbox(
        "Cost Code - Description", COST_CODES["id"],
        format_func=lambda x: f"{COST_CODES.loc[COST_CODES.id == x, 'code'].iloc[0]} - {COST_CODES.loc[COST_CODES.id == x, 'description'].iloc[0]}"
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
st.subheader("📝 Edit Past Entries")
# Prepare entries with job names
ENTRIES = ENTRIES.reset_index(drop=True)
entries = ENTRIES.merge(
    JOBS[["id","name"]], left_on="job_id", right_on="id", how="left"
).rename(columns={"name": "job_name"})

# Filter by Job
job_opts = [None] + list(JOBS["id"])
job_filter = st.selectbox(
    "Filter by Job", job_opts,
    format_func=lambda x: "All Jobs" if x is None else JOBS.loc[JOBS.id == x, "name"].iloc[0]
)
if job_filter is not None:
    entries = entries[entries.job_id == job_filter]

# Editable table
edited = st.data_editor(
    entries,
    use_container_width=True
)

if st.button("Save All Edits"):
    # Drop merge columns
    df2 = edited.drop(columns=["job_name","id"])
    # Apply updates back to ENTRIES
    ENTRIES.loc[df2.index, df2.columns] = df2
    ENTRIES.to_csv("entries.csv", index=False)
    st.success("All edits saved!")

# --- Reporting ---
st.header("Performance Report")
sel = st.selectbox(
    "Select Job for Report", JOBS["id"],
    format_func=lambda x: JOBS.loc[JOBS.id == x, "name"].iloc[0]
)
df = ENTRIES[ENTRIES.job_id == sel].copy()
if not df.empty:
    df = df.merge(
        COST_CODES[["id", "pmph_goal"]],
        left_on="cost_code_id", right_on="id"
    )
    df["estimated"] = df["hours"] * df["pmph_goal"]
    df["variance"] = df["units_installed"] - df["estimated"]
    st.dataframe(
        df[["date","cost_code_id","job_id","hours","units_installed","estimated","variance"]]
    )
    st.line_chart(
        df.set_index("date")[ ["units_installed","estimated","variance"] ]
    )
else:
    st.info("No entries for this job yet.")
