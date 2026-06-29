import streamlit as st
from utils.ui import page_header, section, kpi_row, divider
from utils.bigquery_client import run_query, gold
from utils import charts


def render():
    page_header(
        "Sequential Rules",
        "Thuật toán CPT+ — các luật chuỗi hành vi mua sắm phổ biến",
    )

    with st.spinner("Đang tải..."):
        df_kpi = run_query(f"""
            SELECT COUNT(*) AS total_rules,
                   ROUND(AVG(confidence), 4) AS avg_conf,
                   ROUND(MAX(confidence), 4) AS max_conf,
                   ROUND(MIN(confidence), 4) AS min_conf
            FROM {gold('gold_sequential_rules')}
        """)
        df_rules = run_query(f"""
            SELECT antecedent, consequent, pattern_length, rank,
                   ROUND(confidence, 4) AS confidence
            FROM {gold('gold_sequential_rules')}
            ORDER BY confidence DESC LIMIT 100
        """)
        df_conf_dist = run_query(f"""
            SELECT ROUND(confidence, 2) AS conf_bin, COUNT(*) AS n
            FROM {gold('gold_sequential_rules')}
            GROUP BY conf_bin ORDER BY conf_bin
        """)
        df_len = run_query(f"""
            SELECT pattern_length, COUNT(*) AS n, ROUND(AVG(confidence),4) AS avg_conf
            FROM {gold('gold_sequential_rules')}
            GROUP BY pattern_length ORDER BY pattern_length
        """)
        df_cons = run_query(f"""
            SELECT consequent, COUNT(*) AS n, ROUND(AVG(confidence),4) AS avg_conf
            FROM {gold('gold_sequential_rules')}
            GROUP BY consequent ORDER BY n DESC LIMIT 12
        """)

    k = df_kpi.iloc[0]
    kpi_row([("Tổng luật", f"{k['total_rules']:,.0f}"),
             ("Avg Confidence", f"{k['avg_conf']:.4f}"),
             ("Max Confidence", f"{k['max_conf']:.4f}"),
             ("Min Confidence", f"{k['min_conf']:.4f}")])
    divider()

    section("Top 10 luật — Confidence cao nhất")
    df_top = df_rules.head(10).copy()
    df_top["label"] = df_top["antecedent"] + " → " + df_top["consequent"]
    fig = charts.bar(df_top, x="confidence", y="label", orientation="h")
    fig.update_layout(yaxis=dict(autorange="reversed"), height=360,
                      xaxis_title="Confidence", xaxis_range=[0, 1], yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
    divider()

    col_a, col_b = st.columns(2)
    with col_a:
        section("Phân bố Confidence")
        fig = charts.bar(df_conf_dist, x="conf_bin", y="n")
        fig.update_layout(xaxis_title="Confidence", yaxis_title="Số luật")
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        section("Phân bố độ dài chuỗi")
        fig = charts.bar(df_len, x="pattern_length", y="n", color="#C8102E")
        fig.update_layout(xaxis_title="Pattern Length", yaxis_title="Số luật", xaxis_dtick=1)
        st.plotly_chart(fig, use_container_width=True)
    divider()

    section("Consequent phổ biến nhất")
    fig = charts.bar(df_cons, x="n", y="consequent", orientation="h", color="#FF6B6B")
    fig.update_layout(yaxis=dict(autorange="reversed"), height=380,
                      xaxis_title="Số lần xuất hiện", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)
    divider()

    section("Bảng tra cứu luật (Top 100)")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        min_conf = st.slider("Confidence tối thiểu", 0.0, 1.0, 0.0, 0.01)
    with col_f2:
        kw = st.text_input("Tìm kiếm sản phẩm", placeholder="Ví dụ: Trousers...")
    df_f = df_rules[df_rules["confidence"] >= min_conf]
    if kw:
        mask = (df_f["antecedent"].str.contains(kw, case=False, na=False) |
                df_f["consequent"].str.contains(kw, case=False, na=False))
        df_f = df_f[mask]
    df_f = df_f.rename(columns={"antecedent": "Antecedent", "consequent": "Consequent",
                                 "pattern_length": "Length", "rank": "Rank",
                                 "confidence": "Confidence"})
    st.caption(f"{len(df_f)} luật")
    st.dataframe(df_f, use_container_width=True, hide_index=True)
