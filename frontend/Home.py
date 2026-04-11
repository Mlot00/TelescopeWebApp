import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("TWAPP_API_BASE_URL", "http://api:8000")

st.set_page_config(page_title="TelescopeWebApp", layout="wide")
st.title("TelescopeWebApp")
st.caption("Szkielet aplikacji do analiz DL3 (theta², sky map, spectrum, light curve)")

st.write("### Status backendu")
try:
    response = requests.get(f"{API_BASE_URL}/health", timeout=3)
    response.raise_for_status()
    st.success(f"API działa: {response.json()}")
except Exception as exc:
    st.warning(f"Nie można połączyć się z API ({API_BASE_URL}): {exc}")

st.write("### Moduły")
st.markdown(
    """
- Theta²
- Sky Map
- Spectrum
- Light Curve

Każda podstrona wysyła request do odpowiedniego endpointu API.
"""
)
