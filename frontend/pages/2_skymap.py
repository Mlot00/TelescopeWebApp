import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("TWAPP_API_BASE_URL", "http://localhost:8000")

st.title("Sky Map")
dataset_id = st.text_input("Dataset ID", value="crab_sample")
width_deg = st.number_input("Szerokość [deg]", min_value=0.1, value=2.0)
binsz_deg = st.number_input(
    "Bin size [deg]",
    min_value=0.001,
    value=0.02,
    step=0.001,
    format="%.3f",
)

if st.button("Uruchom"):
    payload = {"dataset_id": dataset_id, "width_deg": width_deg, "binsz_deg": binsz_deg}
    response = requests.post(f"{API_BASE_URL}/skymap", json=payload, timeout=30)
    st.json(response.json())
