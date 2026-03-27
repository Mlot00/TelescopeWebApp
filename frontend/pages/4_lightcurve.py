import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("TWAPP_API_BASE_URL", "http://localhost:8000")

st.title("Light Curve")
dataset_id = st.text_input("Dataset ID", value="crab_sample")
e_min = st.number_input("E min [TeV]", min_value=0.001, value=0.05)
e_max = st.number_input("E max [TeV]", min_value=0.01, value=20.0)
time_bin = st.selectbox("Binning czasowy", options=["5min", "30min", "1h", "1d"], index=3)

if st.button("Uruchom"):
    payload = {
        "dataset_id": dataset_id,
        "e_min_tev": e_min,
        "e_max_tev": e_max,
        "time_bin": time_bin,
    }
    response = requests.post(f"{API_BASE_URL}/lightcurve", json=payload, timeout=30)
    st.json(response.json())
