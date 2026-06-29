import streamlit as st
from utils.bigquery_client import run_queries_parallel, gold
from utils.ui import page_header, section, kpi_row, divider
from utils import charts


def render():
    page_header(
        "Phân tích khách hàng",
        "Phân bố độ tuổi, nhóm tuổi và trạng thái thành viên câu lạc bộ H&M",
    )

    with st.spinner("Đang tải dữ liệu..."):
        data = run_queries_parallel({
            "kpi": f"""
                SELECT
                    COUNT(DISTINCT customer_id)             AS total_customers,
                    ROUND(AVG(NULLIF(age, 0)), 1)           AS avg_age,
                    COUNTIF(is_active = TRUE)               AS active_members,
                    ROUND(COUNTIF(is_active = TRUE) * 100.0 / COUNT(*), 1) AS active_pct
                FROM {gold('dim_customers')}
            """,
            "age_dist": f"""
                SELECT age
                FROM {gold('dim_customers')}
                WHERE age > 0 AND age < 100
            """,
            "age_group": f"""
                SELECT age_group, COUNT(*) AS customers
                FROM {gold('dim_customers')}
                WHERE age_group IS NOT NULL
                GROUP BY age_group
                ORDER BY customers DESC
            """,
            "club": f"""
                SELECT COALESCE(club_member_status, 'Unknown') AS status, COUNT(*) AS customers
                FROM {gold('dim_customers')}
                GROUP BY club_member_status
                ORDER BY customers DESC
            """,
            "age_revenue": f"""
                SELECT
                    age_group,
                    ROUND(SUM(price_sek), 0)    AS revenue,
                    COUNT(*)                    AS transactions
                FROM {gold('fact_sales')}
                WHERE age_group IS NOT NULL
                GROUP BY age_group
                ORDER BY revenue DESC
            """,
        })

    df_kpi        = data["kpi"]
    df_age_dist   = data["age_dist"]
    df_age_group  = data["age_group"]
    df_club       = data["club"]
    df_age_revenue = data["age_revenue"]

    k = df_kpi.iloc[0]
    kpi_row([
        ("Tổng khách hàng",   f"{k['total_customers']:,.0f}"),
        ("Tuổi trung bình",   f"{k['avg_age']:.1f}"),
        ("Thành viên active", f"{k['active_members']:,.0f}"),
        ("Tỷ lệ active",      f"{k['active_pct']:.1f}%"),
    ])

    divider()

    col_a, col_b = st.columns(2)
    with col_a:
        section("Phân bố độ tuổi")
        fig = charts.histogram(df_age_dist, x="age", nbins=40)
        fig.update_layout(xaxis_title="Tuổi", yaxis_title="Số khách hàng")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        section("Trạng thái thành viên")
        fig = charts.pie(df_club, names="status", values="customers")
        st.plotly_chart(fig, use_container_width=True)

    divider()

    col_c, col_d = st.columns(2)
    with col_c:
        section("Số khách hàng theo nhóm tuổi")
        fig = charts.bar(df_age_group, x="age_group", y="customers")
        fig.update_layout(xaxis_title="", yaxis_title="Khách hàng")
        st.plotly_chart(fig, use_container_width=True)

    with col_d:
        section("Doanh thu theo nhóm tuổi")
        fig = charts.bar(df_age_revenue, x="age_group", y="revenue", color="#C8102E")
        fig.update_layout(xaxis_title="", yaxis_title="SEK")
        st.plotly_chart(fig, use_container_width=True)

    divider()

    section("Chi tiết nhóm tuổi")
    merged = df_age_group.merge(df_age_revenue, on="age_group", how="left")
    merged.columns = ["Nhóm tuổi", "Khách hàng", "Doanh thu (SEK)", "Giao dịch"]
    st.dataframe(merged, use_container_width=True, hide_index=True)
