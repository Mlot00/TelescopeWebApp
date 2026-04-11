import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("TWAPP_API_BASE_URL", "http://api:8000")

st.title("Theta²")
dataset_id = st.text_input("Dataset ID", value="crab_sample")
theta2_max = st.number_input("theta2 max", min_value=0.01, value=0.3, step=0.01)
n_bins = st.number_input("Liczba binów", min_value=5, max_value=300, value=30)

if st.button("Uruchom"):
    payload = {"dataset_id": dataset_id, "theta2_max": theta2_max, "n_bins": int(n_bins)}
    response = requests.post(f"{API_BASE_URL}/theta2", json=payload, timeout=30)
    st.json(response.json())
