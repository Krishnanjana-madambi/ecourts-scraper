# app.py
import streamlit as st
import os
import json
from datetime import date
from ecourts_scraper import fetch_cause_list_pdf

st.set_page_config(page_title="eCourts Cause List Scraper", layout="wide")
st.title("📄 eCourts Cause List Scraper")

# --- Input selections ---
state = st.text_input("State", "Delhi")
district = st.text_input("District", "New Delhi")
court_complex = st.text_input("Court Complex", "District Court Complex")
date_str = st.text_input("Date (dd-mm-yyyy)", date.today().strftime("%d-%m-%Y"))
civil_or_criminal = st.selectbox("Case Type", ["Civil", "Criminal"])

run_scraper = st.button("Fetch Cause List PDF")

if run_scraper:
    st.info("Running scraper... Please check terminal for captcha input.")
    
    try:
        fetch_cause_list_pdf(state, district, court_complex, date_str, civil_or_criminal)
    except Exception as e:
        st.error(f"An error occurred: {e}")

    # Show manifest JSON if exists
    manifest_path = os.path.join("output", f"{date_str}_manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        st.success("Scraper finished! Manifest JSON:")
        st.json(data)
        
        # List downloaded PDFs
        st.write("Downloaded PDFs:")
        for item in data.get("downloads", []):
            st.write(f"- {item['court']}: {item['file']}")
    else:
        st.warning("No manifest found. Did the scraper run correctly?")

# --- Optional alert info ---
st.info("⚠️ If the scraper shows an alert like 'Select Establishment', check terminal and dismiss if prompted.")
