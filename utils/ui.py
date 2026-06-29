"""Shared UI helpers — keeps pages DRY."""
import streamlit as st


def page_header(title: str, subtitle: str = ""):
    st.markdown(f'<div class="pg-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="pg-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def section(label: str):
    st.markdown(f'<div class="sec-label">{label}</div>', unsafe_allow_html=True)


def kpi_row(items: list):
    """items = list of (label, value, sub) tuples. sub is optional."""
    cards = ""
    for item in items:
        label = item[0]
        value = item[1]
        sub   = item[2] if len(item) > 2 else ""
        sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
        cards += (
            f'<div class="kpi">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'{sub_html}'
            f'</div>'
        )
    st.markdown(f'<div class="kpi-row">{cards}</div>', unsafe_allow_html=True)


def divider():
    st.markdown('<hr class="divider">', unsafe_allow_html=True)


def placeholder(title: str, body: str):
    st.markdown(
        f'<div class="placeholder-box"><h3>{title}</h3><p>{body}</p></div>',
        unsafe_allow_html=True,
    )
