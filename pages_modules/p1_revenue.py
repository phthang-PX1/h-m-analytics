import streamlit as st
from utils.bigquery_client import run_queries_parallel, gold
from utils.ui import page_header, section, kpi_row, divider
from utils import charts


def render():
    page_header(
        "Tổng quan doanh thu",
        "Dữ liệu giao dịch H&M — kênh bán, xu hướng theo thời gian và ngành hàng",
    )

    with st.spinner("Đang tải dữ liệu..."):
        data = run_queries_parallel({
            "kpi": f"""
                SELECT
                    COUNT(*)                        AS total_transactions,
                    COUNT(DISTINCT customer_id)     AS total_customers,
                    COUNT(DISTINCT article_id)      AS total_articles,
                    ROUND(SUM(price_sek), 0)        AS total_revenue,
                    ROUND(AVG(price_sek), 2)        AS avg_price
                FROM {gold('fact_sales')}
            """,
            "channel": f"""
                SELECT
                    sales_channel               AS channel,
                    COUNT(*)                    AS transactions,
                    ROUND(SUM(price_sek), 0)    AS revenue
                FROM {gold('fact_sales')}
                GROUP BY sales_channel
            """,
            "monthly": f"""
                SELECT
                    FORMAT_TIMESTAMP('%Y-%m', transaction_at)   AS month,
                    ROUND(SUM(price_sek), 0)                    AS revenue
                FROM {gold('fact_sales')}
                GROUP BY month
                ORDER BY month
            """,
            "index": f"""
                SELECT
                    index_group,
                    ROUND(SUM(price_sek), 0)    AS revenue
                FROM {gold('fact_sales')}
                WHERE index_group IS NOT NULL
                GROUP BY index_group
                ORDER BY revenue DESC
                LIMIT 10
            """,
        })

    df_kpi     = data["kpi"]
    df_channel = data["channel"]
    df_monthly = data["monthly"]
    df_index   = data["index"]

    k = df_kpi.iloc[0]
    kpi_row([
        ("Tổng doanh thu", f"{k['total_revenue']:,.0f} SEK"),
        ("Giao dịch",      f"{k['total_transactions']:,.0f}"),
        ("Khách hàng",     f"{k['total_customers']:,.0f}"),
        ("Sản phẩm",       f"{k['total_articles']:,.0f}"),
        ("Giá trung bình", f"{k['avg_price']:,.2f} SEK"),
    ])

    divider()

    col_a, col_b = st.columns([1, 2])
    with col_a:
        section("Cơ cấu doanh thu theo kênh")
        fig = charts.pie(df_channel, names="channel", values="revenue")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        section("Doanh thu theo tháng")
        fig = charts.line(df_monthly, x="month", y="revenue")
        fig.update_layout(xaxis_title="", yaxis_title="SEK")
        st.plotly_chart(fig, use_container_width=True)

    divider()

    section("Doanh thu theo ngành hàng")
    fig = charts.bar(df_index, x="revenue", y="index_group", orientation="h")
    fig.update_layout(yaxis=dict(autorange="reversed"), height=320, xaxis_title="SEK", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    divider()

    section("Chi tiết theo kênh bán")
    df_channel.columns = ["Kênh bán", "Giao dịch", "Doanh thu (SEK)"]
    st.dataframe(df_channel, use_container_width=True, hide_index=True)
