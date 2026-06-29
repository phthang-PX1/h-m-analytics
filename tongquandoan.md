# BÁO CÁO TÓM TẮT ĐỒ ÁN MÔN HỌC
**Môn:** Nhà kho dữ liệu và tích hợp (UEL)  
**Giảng viên hướng dẫn:** TS. Nguyễn Thôn Dã

---

## 1. THÔNG TIN CHUNG
* **Tên đề tài:** Hệ thống Data Lakehouse phân tích chuỗi hành vi và gợi ý sản phẩm cá nhân hóa cho chuỗi bán lẻ thời trang H&M.
* **Lĩnh vực ứng dụng:** Hệ thống thông tin quản lý (MIS), Bán lẻ (Retail), Thương mại điện tử (E-commerce).
* **Nguồn dữ liệu:** `dinhlnd1610/HM-Personalized-Fashion-Recommendations` (Hugging Face Hub).
* **Hệ sinh thái công nghệ sử dụng:** Google BigQuery + dbt Cloud + Google Colab + Streamlit + Llama 3 (via Groq API).

---

## 2. KIẾN TRÚC DỮ LIỆU ĐẦU VÀO (DATA INPUT SCHEMA)
Hệ thống tiếp nhận dữ liệu thô quy mô lớn với tổng cộng hơn 31.7 triệu dòng giao dịch từ 3 cấu phần chính:

### a. Cấu phần Sản phẩm (`articles`) - 105,542 bản ghi
Cung cấp ngữ nghĩa chi tiết cho các mặt hàng, bao gồm:
* `article_id` (int64) - Khóa chính.
* `prod_name` (string) - Tên sản phẩm.
* `product_type_name` (string) - Loại mặt hàng (Trousers, Dress, T-shirt...).
* `product_group_name` (string) - Nhóm hàng tổng quát.
* `index_group_name` (string) - Phân cấp ngành hàng (Ladieswear, Menswear, Sportswear...).
* `colour_group_name` (string) - Màu sắc gốc.
* `graphical_appearance_name` (string) - Mô tả họa tiết (Trơn, sọc, hoa...).
* `detail_desc` (string) - Đoạn văn bản mô tả đặc tính chi tiết của sản phẩm.

### b. Cấu phần Khách hàng (`customers`) - 1,371,980 bản ghi
Lưu trữ thuộc tính nền tảng của người dùng:
* `customer_id` (string) - Khóa chính.
* `age` (float64) - Độ tuổi khách hàng.
* `club_member_status` (string) - Trạng thái thành viên CLB H&M.

### c. Cấu phần Giao dịch (`transactions`) - 31,788,324 bản ghi
Nhật ký hành vi thời gian thực ở mức chi tiết nhất (Atomic level):
* `t_dat` (string) - Mốc thời gian phát sinh giao dịch.
* `customer_id` (string) - Khóa ngoại kết nối với bảng khách hàng.
* `article_id` (int64) - Khóa ngoại kết nối với bảng sản phẩm.
* `price` (float64) - Giá tiền sản phẩm tại thời điểm mua.
* `sales_channel_id` (int64) - Kênh thực hiện giao dịch (1: Online, 2: Offline Store).

---

## 3. KHUNG KIẾN TRÚC VÀ ĐƯỜNG ỐNG DỮ LIỆU (MEDALLION)
Dữ liệu di chuyển khép kín và tự động hóa qua các phân tầng vật lý trên **Google BigQuery** dưới sự điều phối và biến đổi của **dbt Cloud**:

* **Tầng Bronze (Dữ liệu thô):** Script Python `ingest.py` kéo 3 bảng (`articles`, `customers`, `transactions`) từ Hugging Face Hub (`dinhlnd1610/HM-Personalized-Fashion-Recommendations`).
  * *Bronze Persistence (Data Lake):* Lưu thành file `.parquet` bảo toàn nguyên bản dữ liệu thô phục vụ dự phòng.
  * *Bronze Warehouse (Data Warehouse):* Nạp vào BigQuery `Dataset1_Bronze` phục vụ truy vấn.
* **Tầng Silver (Làm sạch & Chuẩn hóa):** dbt Cloud thực hiện cấu hình các luật làm sạch thông qua mã SQL:
  * Áp dụng hàm `COALESCE(age, 0)` để lấp đầy các ô dữ liệu tuổi bị khuyết thiếu.
  * Áp dụng hàm `CAST(t_dat AS TIMESTAMP)` để chuẩn hóa chuỗi ngày tháng, phục vụ phân tích chuỗi.
  * Lọc dữ liệu lỗi (`WHERE price > 0`), loại bỏ các khóa NULL và đổi tên cột tường minh.
* **Tầng Gold (Mô hình hóa Kimball Star Schema):** dbt Cloud tổ chức dữ liệu phục vụ phân tích và AI:
  * `fact_sales`: Chứa nhật ký giao dịch chi tiết, doanh thu thực tế.
  * `dim_products`: Giữ nguyên các trường text tiếng Anh (`prod_name`, `product_type_name`, `detail_desc`) phục vụ mô hình ngôn ngữ lớn (LLM) đọc hiểu ngữ nghĩa.
  * `dim_customers`: Chứa thông tin khách hàng kèm logic phân nhóm tuổi (`age_group`).
  * Các bảng rộng (`Wide Tables`) phục vụ AI: `wide_ai_sequences` (chuỗi hành vi theo thời gian) và `wide_ai_features` (đặc trưng tổng hợp của mỗi khách hàng).

---

## 4. CHI TIẾT SẢN PHẨM ĐẦU RA THEO PHÂN CÔNG (DELIVERABLES)

### Khối 1: Tiền xử lý và Khám phá dữ liệu (EDA)
* **Yêu cầu phân tích:** Thực hiện thống kê và vẽ biểu đồ trực quan hóa trên Google Colab để tìm hiểu 5 khía cạnh lớn của dữ liệu: Chất lượng dữ liệu (tỉ lệ NULL, rác), Hành vi mua hàng, Phân bố khách hàng (tuổi, câu lạc bộ), Phân bố sản phẩm (màu sắc, họa tiết, ngành hàng), và Phân tích giao dịch (giá, doanh thu theo kênh Online/Store).
* **Sản phẩm bàn giao:** **Bảng tổng hợp đối chiếu logic**. Liệt kê rõ: *EDA phát hiện ra vấn đề gì ở dữ liệu thô $\rightarrow$ Thiết lập kỹ thuật tiền xử lý/làm sạch tương ứng thế nào ở tầng Silver $\rightarrow$ Thống kê chính xác số lượng dòng dữ liệu sau khi xử lý*.

### Khối 2: Huấn luyện Trí tuệ nhân tạo (AI/ML Layer)
Triển khai khép kín hai luồng mô hình trên môi trường Google Colab và ghi kết quả ngược lại kho Gold trên BigQuery:

1. **Luồng 1 - Khai phá chuỗi hành vi (Thuật toán CPT+):**
   * *Đầu vào:* Bảng dữ liệu chuỗi tuần tự `wide_ai_sequences`.
   * *Xử lý:* Huấn luyện mô hình cây nén dự đoán chuỗi CPT+ (Compressed Prediction Tree) để tìm các quy luật mua sắm lặp lại theo thời gian.
   * *Đầu ra:* Sinh toàn bộ các luật chuỗi phổ biến (Ví dụ: Mua `<Áo thun>` $\rightarrow$ sẽ mua tiếp `<Quần short>`). Xuất thành DataFrame và ghi trực tiếp vào bảng vật lý **`gold_sequential_rules`** trên BigQuery.
   * *Đánh giá:* Liệt kê Top 10 rules có độ chính xác (Confidence) cao nhất kèm biểu đồ thanh nhận xét.
2. **Luồng 2 - Hệ thống gợi ý sản phẩm (Mô hình LightFM):**
   * *Đầu vào:* Kết hợp ma trận tương tác khách hàng - sản phẩm (`Interaction matrix`) + Thu thuộc tính từ `wide_ai_features` + Làm giàu đặc trưng bằng luật chuỗi tuần tự đầu ra của Luồng 1.
   * *Xử lý:* Huấn luyện mô hình học máy kết hợp Hybrid (LightFM) với hàm loss WARP tối ưu cho bài toán thương mại điện tử.
   * *Đầu ra:* Sinh danh sách Top-5 sản phẩm gợi ý cá nhân hóa cho toàn bộ tệp khách hàng. Ghi kết quả vào bảng vật lý **`gold_recommendations`** trên BigQuery.
   * *Đánh giá đối chiếu (Baseline Comparison):* Xây dựng thêm một mô hình nền tảng đơn giản dựa trên độ phổ biến mặt hàng (**Popularity Baseline**) để so sánh hiệu năng thông qua chỉ số độ phủ `Coverage@5` nhằm chứng minh giá trị cải tiến của mô hình AI chính. Xuất bảng demo thực tế kết quả Top-5 gợi ý của 3-5 khách hàng đại diện.

### Khối 3: Tầng ứng dụng hỗ trợ ra quyết định (Dashboard & GenBI)
Tầng giao diện kết nối trực tiếp vào các bảng Gold trên BigQuery để xử lý hai bài toán quản trị:

1. **Visual Analytics (Ứng dụng Streamlit):** Thiết kế hệ thống báo cáo tĩnh trực quan hóa gồm 5 trang chuyên biệt:
   * *Trang 1 - Tổng quan doanh thu:* Hiển thị các thẻ chỉ số KPI động, cơ cấu doanh thu theo kênh bán (Online/Store) và biểu đồ ngành hàng thời trang.
   * *Trang 2 - Phân tích khách hàng:* Trực quan hóa phân bố độ tuổi, nhóm tuổi và trạng thái thành viên câu lạc bộ H&M.
   * *Trang 3 - Phân tích sản phẩm:* Thống kê các mặt hàng bán chạy, cơ cấu màu sắc và họa tiết thiết kế.
   * *Trang 4 - Gợi ý sản phẩm:* Tạo bộ lọc động theo `customer_id` để kết nối và gọi ra danh sách Top-5 sản phẩm cá nhân hóa lấy từ bảng `gold_recommendations`.
   * *Trang 5 - Sequential Rules:* Hiển thị bảng tổng hợp các luật chuỗi hành vi tuần tự và biểu đồ phân tích độ tin cậy.
   *(Lưu ý kỹ thuật: Toàn bộ các biểu đồ trên Streamlit phải được tính toán thông qua việc thiết lập các chỉ số **Measure DAX cơ bản** như SUM, COUNT, DISTINCTCOUNT để tối ưu hiệu năng).*
2. **Generative BI (Ứng dụng Streamlit + Llama 3):** Xây dựng cổng tương tác ngôn ngữ tự nhiên chạy local:
   * Sử dụng Groq SDK để tích hợp mô hình ngôn ngữ lớn **Llama 3**.
   * Thiết lập cấu trúc **System Prompt** chi tiết mô tả rõ ràng schema định dạng bằng tiếng Anh tường minh của các bảng dữ liệu tầng Gold.
   * Vận hành luồng xử lý: Người quản lý gõ câu hỏi tiếng Việt/tiếng Anh $\rightarrow$ Llama 3 tự động biên dịch thành mã SQL chuẩn xác $\rightarrow$ Truy vấn trực tiếp xuống BigQuery $\rightarrow$ Streamlit tiếp nhận bảng kết quả và hiển thị câu trả lời tư vấn kinh doanh cho nhà quản trị.
   * Kiểm thử thành công tối thiểu 5 câu hỏi mẫu thực tế không phát sinh lỗi cú pháp SQL.