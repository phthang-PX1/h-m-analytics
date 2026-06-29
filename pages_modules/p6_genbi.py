import streamlit as st
import re
from utils.bigquery_client import run_query_uncached
from utils.ui import page_header, section, divider

SYSTEM_PROMPT = """You are an expert SQL analyst for H&M's Data Lakehouse on Google BigQuery.
Convert the user's natural language question into a valid BigQuery SQL query.

PROJECT : project-group4-id
DATASET : Dataset1_Silver_Dataset1_Gold

TABLE SCHEMAS:

fact_sales  (wide table, pre-joined — do NOT join with other tables)
  transaction_at     TIMESTAMP
  customer_id        STRING
  article_id         INTEGER
  price_sek          FLOAT        revenue = SUM(price_sek)
  sales_channel      STRING       'Online' | 'Store'
  product_name       STRING
  product_type       STRING
  product_group      STRING
  index_group        STRING
  colour_group       STRING
  age                INTEGER
  age_group          STRING
  club_member_status STRING

dim_customers
  customer_id, age INTEGER, age_group, club_member_status,
  is_subscribed_fn BOOLEAN, is_active BOOLEAN

dim_products
  article_id INTEGER, product_name, product_type, product_group,
  index_group, colour_group, graphical_appearance, detail_description

gold_recommendations  (wide: one row per customer)
  customer_id, top_1 INTEGER, top_2, top_3, top_4, top_5

gold_sequential_rules
  antecedent, consequent, pattern_length INTEGER, rank INTEGER, confidence FLOAT

wide_ai_features
  customer_id, age, age_group, club_member_status,
  total_transactions, unique_products_bought, total_spending,
  avg_price_per_item, first_purchase_date, last_purchase_date,
  online_count, store_count, preferred_channel,
  top_index_group, top_colour_group

wide_ai_sequences
  customer_id, age_group, article_id, product_type, product_group,
  index_group, colour_group, sales_channel, transaction_at,
  purchase_sequence_number

RULES:
- Always prefix tables: `project-group4-id.Dataset1_Silver_Dataset1_Gold.<table>`
- fact_sales is pre-joined — NEVER JOIN it with dim_products or dim_customers
- Monthly grouping: FORMAT_TIMESTAMP('%Y-%m', transaction_at)
- Revenue: ROUND(SUM(price_sek), 2)
- Always name columns explicitly — no SELECT *
- Add LIMIT 1000 unless user asks for all data
- Output raw SQL only — no explanation, no markdown fences
"""

SAMPLES = [
    "Top 5 sản phẩm bán chạy nhất?",
    "Doanh thu theo từng tháng năm 2020?",
    "Nhóm tuổi nào chi tiêu nhiều nhất?",
    "Tỷ lệ doanh thu kênh Online vs Store?",
    "Màu sắc nào được mua nhiều nhất?",
    "Số giao dịch trung bình của khách Active?",
]


def _call_llm(question: str, api_key: str) -> str:
    from groq import Groq
    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": question},
        ],
        temperature=0.05,
        max_tokens=1024,
    )
    return resp.choices[0].message.content.strip()


def _clean_sql(raw: str) -> str:
    raw = re.sub(r"```sql", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```", "", raw)
    return raw.strip()


def _run(question: str, api_key: str):
    """Execute LLM → SQL → BigQuery and display results."""
    st.markdown(f"**Câu hỏi:** {question}")

    with st.spinner("Đang tạo SQL..."):
        try:
            sql = _clean_sql(_call_llm(question, api_key))
        except Exception as e:
            st.error(f"Lỗi LLM: {e}")
            return

    with st.expander("SQL được tạo", expanded=True):
        st.code(sql, language="sql")

    with st.spinner("Đang truy vấn BigQuery..."):
        try:
            df = run_query_uncached(sql)
        except Exception as e:
            st.error(f"Lỗi truy vấn: {e}")
            return

    st.caption(f"{len(df)} dòng kết quả")
    st.dataframe(df, use_container_width=True, hide_index=True)


def render():
    page_header(
        "Generative SQL Query",
        "Hỏi bằng tiếng Việt hoặc tiếng Anh — Llama 3.3 tạo SQL, BigQuery trả kết quả",
    )

    # ── API key ──────────────────────────────────────────────────────────────
    try:
        api_key = st.secrets["groq_api_key"]
    except Exception:
        api_key = ""

    if not api_key:
        api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
        if not api_key:
            st.caption("Lấy key miễn phí tại console.groq.com")
            return

    divider()

    # ── Session state init ────────────────────────────────────────────────
    if "gbi_input" not in st.session_state:
        st.session_state.gbi_input = ""
    if "gbi_submitted" not in st.session_state:
        st.session_state.gbi_submitted = False

    # ── Sample buttons — set input và submit luôn ─────────────────────────
    section("Câu hỏi gợi ý")
    cols = st.columns(3)
    for i, q in enumerate(SAMPLES):
        if cols[i % 3].button(q, key=f"sq_{i}", use_container_width=True):
            st.session_state.gbi_input = q
            st.session_state.gbi_submitted = True
            st.rerun()

    divider()

    # ── Text input ────────────────────────────────────────────────────────
    question = st.text_area(
        "Câu hỏi",
        value=st.session_state.gbi_input,
        placeholder="Ví dụ: Doanh thu tháng nào cao nhất năm 2020?",
        height=72,
        label_visibility="collapsed",
    )

    if st.button("Gửi", type="primary", use_container_width=True):
        if question.strip():
            st.session_state.gbi_input = question.strip()
            st.session_state.gbi_submitted = True
            st.rerun()

    # ── Execute nếu có submitted ──────────────────────────────────────────
    if st.session_state.gbi_submitted and st.session_state.gbi_input:
        q = st.session_state.gbi_input
        st.session_state.gbi_submitted = False   # reset để không chạy lại
        _run(q, api_key)
