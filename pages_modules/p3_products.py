import streamlit as st
from utils.bigquery_client import run_queries_parallel, gold
from utils.ui import page_header, section, kpi_row, divider
from utils import charts


def render():
    page_header(
        "Phân tích sản phẩm",
        "Sản phẩm bán chạy, phân bố màu sắc, họa tiết và doanh thu theo loại hàng",
    )

    with st.spinner("Đang tải dữ liệu..."):
        data = run_queries_parallel({
            "kpi": f"""
                SELECT
                    COUNT(DISTINCT article_id)          AS total_products,
                    COUNT(DISTINCT product_type)        AS total_types,
                    COUNT(DISTINCT index_group)         AS total_groups,
                    COUNT(DISTINCT colour_group)        AS total_colors
                FROM {gold('dim_products')}
            """,
            "top": f"""
                SELECT
                    product_name,
                    product_type,
                    index_group,
                    COUNT(*)                    AS sold_count,
                    ROUND(SUM(price_sek), 0)    AS revenue
                FROM {gold('fact_sales')}
                WHERE product_name IS NOT NULL
                GROUP BY product_name, product_type, index_group
                ORDER BY sold_count DESC
                LIMIT 15
            """,
            "color": f"""
                SELECT colour_group AS color, COUNT(*) AS cnt
                FROM {gold('dim_products')}
                WHERE colour_group IS NOT NULL
                GROUP BY colour_group ORDER BY cnt DESC LIMIT 12
            """,
            "pattern": f"""
                SELECT graphical_appearance AS pattern, COUNT(*) AS cnt
                FROM {gold('dim_products')}
                WHERE graphical_appearance IS NOT NULL
                GROUP BY graphical_appearance ORDER BY cnt DESC LIMIT 12
            """,
            "type_rev": f"""
                SELECT product_type, ROUND(SUM(price_sek), 0) AS revenue
                FROM {gold('fact_sales')}
                WHERE product_type IS NOT NULL
                GROUP BY product_type ORDER BY revenue DESC LIMIT 12
            """,
            "color_rev": f"""
                SELECT colour_group AS color, ROUND(SUM(price_sek), 0) AS revenue
                FROM {gold('fact_sales')}
                WHERE colour_group IS NOT NULL
                GROUP BY colour_group ORDER BY revenue DESC LIMIT 10
            """,
        })

    df_kpi      = data["kpi"]
    df_top      = data["top"]
    df_color    = data["color"]
    df_pattern  = data["pattern"]
    df_type_rev = data["type_rev"]
    df_color_rev = data["color_rev"]

    k = df_kpi.iloc[0]
    kpi_row([
        ("Tổng sản phẩm", f"{k['total_products']:,.0f}"),
        ("Loại sản phẩm", f"{k['total_types']:,.0f}"),
        ("Ngành hàng",    f"{k['total_groups']:,.0f}"),
        ("Màu sắc",       f"{k['total_colors']:,.0f}"),
    ])

    divider()

    section("Top 15 sản phẩm bán chạy nhất")
    fig = charts.bar(df_top, x="sold_count", y="product_name", orientation="h")
    fig.update_layout(yaxis=dict(autorange="reversed"), height=420, xaxis_title="Lượt bán", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    divider()

    col_a, col_b = st.columns(2)
    with col_a:
        section("Phân bố màu sắc")
        fig = charts.pie(df_color, names="color", values="cnt")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        section("Họa tiết phổ biến")
        fig = charts.bar(df_pattern, x="cnt", y="pattern", orientation="h", color="#C8102E")
        fig.update_layout(yaxis=dict(autorange="reversed"), height=360, xaxis_title="Sản phẩm", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    divider()

    col_c, col_d = st.columns(2)
    with col_c:
        section("Doanh thu theo loại sản phẩm")
        fig = charts.bar(df_type_rev, x="product_type", y="revenue")
        fig.update_layout(xaxis_tickangle=-40, xaxis_title="", yaxis_title="SEK")
        st.plotly_chart(fig, use_container_width=True)

    with col_d:
        section("Doanh thu theo màu sắc")
        fig = charts.bar(df_color_rev, x="color", y="revenue", color="#FF6B6B")
        fig.update_layout(xaxis_tickangle=-40, xaxis_title="", yaxis_title="SEK")
        st.plotly_chart(fig, use_container_width=True)

    divider()

    section("Chi tiết sản phẩm bán chạy")
    df_top.columns = ["Tên sản phẩm", "Loại", "Ngành hàng", "Lượt bán", "Doanh thu (SEK)"]
    st.dataframe(df_top, use_container_width=True, hide_index=True)
