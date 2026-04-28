import os
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import streamlit as st

try:
    API_BASE_URL = st.secrets.get("TWAPP_API_BASE_URL", None)
except Exception:
    API_BASE_URL = None

API_BASE_URL = API_BASE_URL or os.getenv(
    "TWAPP_API_BASE_URL",
    "http://localhost:8000"
)

DATASETS = {
    "hess-dl3-dr1 — MSH 15-52 (H.E.S.S.)": "hess-dl3-dr1",
    "crab_sample — Mgławica Kraba (LST-1)": "crab_sample",
}

st.set_page_config(page_title="Mapa nieba", page_icon="🔭", layout="wide")


def slider_input(label, key, min_val, max_val, default, step, fmt="%.2f"):
    if key not in st.session_state:
        st.session_state[key] = default
    if f"{key}_slider" not in st.session_state:
        st.session_state[f"{key}_slider"] = default
    if f"{key}_input" not in st.session_state:
        st.session_state[f"{key}_input"] = default

    def _sync_slider():
        val = st.session_state[f"{key}_slider"]
        st.session_state[key] = val
        st.session_state[f"{key}_input"] = val

    def _sync_input():
        val = st.session_state[f"{key}_input"]
        val = max(min_val, min(max_val, val))
        st.session_state[key] = val
        st.session_state[f"{key}_slider"] = val

    col1, col2 = st.columns([3, 1])

    with col1:
        st.slider(
            label,
            min_value=float(min_val),
            max_value=float(max_val),
            value=float(st.session_state[key]),
            step=float(step),
            key=f"{key}_slider",
            on_change=_sync_slider,
        )

    with col2:
        st.number_input(
            "wartość",
            min_value=float(min_val),
            max_value=float(max_val),
            value=float(st.session_state[key]),
            step=float(step),
            format=fmt,
            key=f"{key}_input",
            on_change=_sync_input,
            label_visibility="collapsed",
        )

    return float(st.session_state[key])


@st.cache_data(ttl=600, show_spinner=False)
def fetch_skymap(api_base_url: str, **kwargs) -> dict:
    try:
        r = requests.post(f"{api_base_url}/skymap", json=kwargs, timeout=300)
    except Exception as e:
        raise RuntimeError(f"Błąd połączenia z API: {e}")

    if r.status_code != 200:
        raise RuntimeError(f"API ERROR {r.status_code}\n\n{r.text}")

    return r.json()


def build_figure(sig_arr: np.ndarray) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6, 5))

    im = ax.imshow(sig_arr, origin="lower", cmap="RdBu_r")
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.set_title("Istotność (σ)")
    plt.tight_layout()
    return fig


st.title("Mapa nieba")
st.caption("Analiza tła pierścieniowego (Ring Background) · Gammapy")
st.divider()

col_ds, _ = st.columns([1, 1])

with col_ds:
    dataset_label = st.selectbox("Zestaw danych", list(DATASETS.keys()))

dataset_id = DATASETS[dataset_label]

st.subheader("Parametry analizy")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### Geometria mapy")
    # Wartość domyślna 3.0
    width_deg = slider_input(
        "Szerokość mapy [°]", "width_deg", 0.5, 5.0, 3.0, 0.5, "%.1f"
    )
    binsz_deg = slider_input(
        "Rozmiar piksela [°]", "binsz_deg", 0.01, 0.5, 0.02, 0.01, "%.2f"
    )

    st.markdown("#### Energia")
    e_min = slider_input(
        "Energia min [TeV]", "e_min", 0.1, 10.0, 0.5, 0.1, "%.1f"
    )
    e_max = slider_input(
        "Energia max [TeV]", "e_max", 1.0, 50.0, 10.0, 1.0, "%.1f"
    )

with col_right:
    st.markdown("#### Tło pierścieniowe")
    ring_r_in = slider_input(
        "Promień wewnętrzny [°]", "ring_r_in", 0.1, 2.0, 0.5, 0.05, "%.2f"
    )
    ring_width = slider_input(
        "Szerokość pierścienia [°]", "ring_width", 0.1, 1.0, 0.3, 0.05, "%.2f"
    )
    exclusion_radius = slider_input(
        "Wykluczenie źródła [°]", "exclusion_radius", 0.1, 1.0, 0.3, 0.05, "%.2f"
    )
    correlation_radius = slider_input(
        "Korelacja [°]", "correlation_radius", 0.01, 0.5, 0.1, 0.01, "%.2f"
    )
    offset_max = slider_input(
        "Max offset [°]", "offset_max", 0.5, 5.0, 2.5, 0.5, "%.1f"
    )

st.divider()

energy_error = e_min >= e_max
col_btn, col_status = st.columns([1, 3])

with col_btn:
    run_btn = st.button(
        "Uruchom analizę",
        type="primary",
        use_container_width=True,
        disabled=energy_error,
    )

with col_status:
    if energy_error:
        st.error("Energia min musi być mniejsza niż energia max.")
    else:
        status_placeholder = st.empty()

if not energy_error and run_btn:
    payload = {
        "dataset_id": dataset_id,
        "width_deg": width_deg,
        "binsz_deg": binsz_deg,
        "energy_min_tev": e_min,
        "energy_max_tev": e_max,
        "ring_r_in_deg": ring_r_in,
        "ring_width_deg": ring_width,
        "exclusion_radius_deg": exclusion_radius,
        "correlation_radius_deg": correlation_radius,
        "offset_max_deg": offset_max,
    }

    try:
        with st.spinner("Trwa analiza..."):
            result = fetch_skymap(API_BASE_URL, **payload)

        st.session_state["result"] = result
        status_placeholder.success("Gotowe")
    except Exception as e:
        status_placeholder.error(str(e))
        st.stop()

if "result" not in st.session_state:
    st.stop()

data  = st.session_state["result"].get("data", st.session_state["result"])
stats = data.get("stats", {})

sig_arr = np.array(data.get("significance"), dtype=float)

fig = build_figure(sig_arr)


st.subheader("Wyniki")
col_stats, col_plot = st.columns(2)

with col_stats:
    st.markdown("#### Statystyki")

    if stats:
        c1, c2 = st.columns(2)
        c1.metric("Zliczenia", int(stats.get("n_counts", 0)))
        c2.metric("Tło", round(stats.get("n_background", 0), 1))

        c3, c4 = st.columns(2)
        c3.metric("Nadmiar", round(stats.get("n_excess", 0), 1))
        c4.metric("Max σ", round(stats.get("significance_max", 0), 2))
    else:
        st.warning("Brak statystyk")

    st.markdown("#### Eksport")

    csv = pd.DataFrame(sig_arr).to_csv(index=False).encode("utf-8")

    buf = BytesIO()
    fig.savefig(buf, format="jpg", dpi=300, bbox_inches="tight")
    buf.seek(0)

    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        st.download_button(
            "Pobierz CSV",
            csv,
            "mapa.csv",
            "text/csv",
            type="primary",
            use_container_width=True,
        )

    with col_btn2:
        st.download_button(
            "Pobierz JPG",
            buf,
            "mapa.jpg",
            "image/jpeg",
            type="primary",
            use_container_width=True,
        )

with col_plot:
    st.markdown("#### Mapa")
    st.pyplot(fig, use_container_width=True)
