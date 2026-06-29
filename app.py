import streamlit as st

st.set_page_config(
    page_title="H&M Analytics",
    page_icon="assets/hm_logo.png" if False else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ── Variables ──────────────────────────────────────────── */
:root {
    --red:   #E50010;
    --dark:  #111111;
    --mid:   #555555;
    --light: #F7F7F7;
    --white: #FFFFFF;
    --border:#E0E0E0;
}

/* ── Reset & base ───────────────────────────────────────── */
html, body, [class*="css"] { font-family: "Inter", sans-serif; }
.block-container { padding: 2rem 2.5rem 3rem; max-width: 1400px; }

/* ── Sidebar ────────────────────────────────────────────── */
[data-testid="stSidebar"] { background: var(--dark) !important; }
[data-testid="stSidebar"] * { color: #CCCCCC !important; }
[data-testid="stSidebar"] .stRadio > label { display: none; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    display: flex;
    align-items: center;
    padding: 9px 14px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.88rem;
    transition: background 0.15s;
    color: #CCCCCC !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.07);
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"],
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] [aria-checked="true"] + div {
    background: rgba(229,0,16,0.18);
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] hr { border-color: #2a2a2a !important; margin: 12px 0; }

/* ── Page header ────────────────────────────────────────── */
.pg-title {
    font-size: 1.45rem;
    font-weight: 700;
    color: var(--dark);
    padding-bottom: 10px;
    border-bottom: 2px solid var(--red);
    margin-bottom: 1.5rem;
}
.pg-subtitle {
    font-size: 0.88rem;
    color: var(--mid);
    margin-top: -1rem;
    margin-bottom: 1.5rem;
}

/* ── Section label ──────────────────────────────────────── */
.sec-label {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--mid);
    margin: 1.4rem 0 0.5rem;
}

/* ── KPI cards ──────────────────────────────────────────── */
.kpi-row { display: flex; gap: 16px; margin-bottom: 1.5rem; flex-wrap: wrap; }
.kpi {
    flex: 1;
    min-width: 140px;
    background: var(--white);
    border: 1px solid var(--border);
    border-top: 3px solid var(--red);
    border-radius: 6px;
    padding: 14px 18px;
}
.kpi-label { font-size: 0.72rem; color: var(--mid); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }
.kpi-value { font-size: 1.65rem; font-weight: 700; color: var(--dark); line-height: 1; }
.kpi-sub   { font-size: 0.75rem; color: var(--mid); margin-top: 3px; }

/* ── Divider ────────────────────────────────────────────── */
.divider { border: none; border-top: 1px solid var(--border); margin: 1.2rem 0; }

/* ── Tables ─────────────────────────────────────────────── */
[data-testid="stDataFrame"] { border-radius: 6px; border: 1px solid var(--border); }

/* ── Buttons ────────────────────────────────────────────── */
.stButton > button {
    border-radius: 4px;
    font-size: 0.83rem;
    border: 1px solid var(--border);
    background: var(--white);
    color: var(--dark);
}
.stButton > button:hover { border-color: var(--red); color: var(--red); background: var(--white); }

/* ── Text input ─────────────────────────────────────────── */
.stTextInput > div > div > input, .stTextArea > div > textarea {
    border-radius: 4px;
    border: 1px solid var(--border);
    font-size: 0.88rem;
}

/* ── Code block ─────────────────────────────────────────── */
.stCode { border-radius: 4px; font-size: 0.82rem; }

/* ── Spinner text ───────────────────────────────────────── */
[data-testid="stSpinner"] p { font-size: 0.83rem; color: var(--mid); }

/* ── Expander ───────────────────────────────────────────── */
details > summary { font-size: 0.85rem; font-weight: 500; }

/* ── Placeholder page ───────────────────────────────────── */
.placeholder-box {
    border: 1px dashed var(--border);
    border-radius: 8px;
    padding: 60px 40px;
    text-align: center;
    color: var(--mid);
    margin-top: 1rem;
}
.placeholder-box h3 { font-size: 1.1rem; color: var(--dark); margin-bottom: 8px; }
.placeholder-box p  { font-size: 0.87rem; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='padding:12px 4px 4px'>"
        "<span style='color:#fff;font-size:1.15rem;font-weight:700;letter-spacing:0.5px'>H&M</span>"
        "<span style='color:#E50010;font-size:1.15rem;font-weight:700'> Analytics</span>"
        "</div>"
        "<div style='color:#888;font-size:0.75rem;padding:0 4px 16px'>Data Lakehouse · Nhóm 4</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<hr>", unsafe_allow_html=True)

    page = st.radio(
        "nav",
        options=[
            "Tổng quan doanh thu",
            "Phân tích khách hàng",
            "Phân tích sản phẩm",
            "Gợi ý sản phẩm",
            "Sequential Rules",
            "Generative Query",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        "<div style='color:#555;font-size:0.72rem;padding:0 4px'>"
        "UEL · Nhà kho dữ liệu & Tích hợp<br>2025</div>",
        unsafe_allow_html=True,
    )

# ── Router ────────────────────────────────────────────────────────────────────
if page == "Tổng quan doanh thu":
    from pages_modules.p1_revenue import render
elif page == "Phân tích khách hàng":
    from pages_modules.p2_customers import render
elif page == "Phân tích sản phẩm":
    from pages_modules.p3_products import render
elif page == "Gợi ý sản phẩm":
    from pages_modules.p4_recommendations import render
elif page == "Sequential Rules":
    from pages_modules.p5_sequential import render
else:
    from pages_modules.p6_genbi import render

render()
