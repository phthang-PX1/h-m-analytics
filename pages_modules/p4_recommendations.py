import streamlit as st
import pandas as pd
from utils.ui import page_header, section, kpi_row, divider
from utils.bigquery_client import run_query, gold


def render():
    page_header(
        "Gợi ý sản phẩm cá nhân hóa",
        "Mô hình LightFM (WARP loss) — Top-5 sản phẩm gợi ý cho từng khách hàng",
    )

    col_s, col_b = st.columns([5, 1])
    with col_s:
        cid = st.text_input("Customer ID", placeholder="Nhập customer_id...",
                            label_visibility="collapsed")
    with col_b:
        search = st.button("Tìm kiếm", use_container_width=True)

    divider()

    with st.spinner("Đang tải..."):
        df_ov = run_query(f"""
            SELECT COUNT(DISTINCT customer_id) AS n
            FROM {gold('gold_recommendations')}
        """)
    kpi_row([("Khách hàng có gợi ý", f"{df_ov.iloc[0]['n']:,.0f}"),
             ("Sản phẩm gợi ý / khách", "5")])
    divider()

    if cid or search:
        _show_customer(cid.strip())
    else:
        _show_demo()


def _show_customer(cid: str):
    if not cid:
        st.info("Nhập Customer ID để tra cứu gợi ý.")
        return

    df = run_query(f"""
        SELECT top_1, top_2, top_3, top_4, top_5
        FROM {gold('gold_recommendations')}
        WHERE customer_id = '{cid}'
        LIMIT 1
    """)

    if df.empty:
        st.warning(f"Không tìm thấy gợi ý cho customer_id: {cid}")
        return

    row = df.iloc[0]
    ids = [int(row[f"top_{i}"]) for i in range(1, 6) if row.get(f"top_{i}") is not None]
    if not ids:
        st.warning("Không có dữ liệu gợi ý.")
        return

    df_prod = run_query(f"""
        SELECT article_id, product_name, product_type, index_group, colour_group
        FROM {gold('dim_products')}
        WHERE article_id IN ({','.join(str(a) for a in ids)})
    """)
    order = {aid: i + 1 for i, aid in enumerate(ids)}
    df_prod["Rank"] = df_prod["article_id"].map(order)
    df_prod = df_prod.sort_values("Rank")[["Rank", "product_name", "product_type", "index_group", "colour_group"]]
    df_prod.columns = ["Rank", "Sản phẩm", "Loại", "Ngành hàng", "Màu sắc"]
    st.dataframe(df_prod, use_container_width=True, hide_index=True)


def _show_demo():
    section("Demo — 5 khách hàng đại diện")
    df = run_query(f"""
        SELECT
            r.customer_id,
            c.age,
            c.age_group,
            c.club_member_status,
            r.top1_name, r.top1_type,
            r.top2_name, r.top2_type,
            r.top3_name, r.top3_type,
            r.top4_name, r.top4_type,
            r.top5_name, r.top5_type
        FROM {gold('gold_recommendations_readable')} r
        LEFT JOIN {gold('dim_customers')} c USING (customer_id)
        LIMIT 5
    """)
    if df.empty:
        st.info("Chưa có dữ liệu demo.")
        return
    for idx, (_, row) in enumerate(df.iterrows(), 1):
        age   = int(row["age"]) if row.get("age") else "?"
        group = row.get("age_group") or "?"
        club  = row.get("club_member_status") or "?"
        label = f"Khách hàng #{idx} — {age} tuổi · {group} · {club}"
        with st.expander(label):
            recs = [{"Rank": f"#{i}", "Sản phẩm": row.get(f"top{i}_name", ""),
                     "Loại": row.get(f"top{i}_type", "")} for i in range(1, 6)]
            st.dataframe(pd.DataFrame(recs), use_container_width=True, hide_index=True)
