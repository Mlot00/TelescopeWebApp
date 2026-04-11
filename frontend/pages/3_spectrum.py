import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("TWAPP_API_BASE_URL", "http://api:8000")

st.title("Spectrum")
dataset_id = st.text_input("Dataset ID", value="crab_sample")
e_min = st.number_input("E min [TeV]", min_value=0.001, value=0.05)
e_max = st.number_input("E max [TeV]", min_value=0.01, value=20.0)
n_bins = st.number_input("Liczba binów", min_value=3, max_value=100, value=12)
instruments_raw = st.text_input("Instrumenty (comma-separated)", value="LST-1")

if st.button("Uruchom"):
    payload = {
        "dataset_id": dataset_id,
        "e_min_tev": e_min,
        "e_max_tev": e_max,
        "n_bins": int(n_bins),
        "instruments": [x.strip() for x in instruments_raw.split(",") if x.strip()],
    }
    response = requests.post(f"{API_BASE_URL}/spectrum", json=payload, timeout=30)
    st.json(response.json())
