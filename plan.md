# Kế Hoạch Xây Dựng Demo FP-Growth Bằng Streamlit

Tài liệu này tập trung vào hệ sinh thái thư viện Python và kiến trúc thiết kế ứng dụng **Streamlit** để demo thuật toán **FP-Growth**.

## 1. Hệ Sinh Thái Thư Viện Python Cho Bản Demo Streamlit

Bảng ánh xạ từ tính năng trong app sang thư viện Python tương ứng để lập trình:

| Thành phần trong App | Thư viện chuẩn nhất | Vai trò cụ thể trong Code | 
| ----- | ----- | ----- | 
| **Giao diện & Thanh trượt (UI)** | `streamlit` | Tạo thanh trượt `st.slider`, hộp chọn `st.multiselect` và chia màn hình thành các `st.tabs` gọn gàng. | 
| **Tiền xử lý & Lõi thuật toán** | `mlxtend`, `pandas` | Dùng `TransactionEncoder` chuẩn hóa dữ liệu; gọi hàm `fpgrowth()`, `apriori()`, `association_rules()`. | 
| **Vẽ cây FP-Tree trực quan** | `graphviz` | Xây dựng class `FPTreeNode` tự định nghĩa và dùng `graphviz.Digraph` để vẽ cây có nút gốc `{null}` và mũi tên nét đứt (vì `mlxtend` không hỗ trợ vẽ cây). | 
| **Biểu đồ & Đồ thị mạng lưới** | `plotly.express`, `pyvis` | Vẽ biểu đồ phân tán 3D (Support - Confidence - Lift) và đồ thị mạng lưới liên kết giữa các mặt hàng. | 
| **Đo lường hiệu năng** | `time`, `tracemalloc` | Đo thời gian thực thi và đỉnh bộ nhớ RAM (Peak Memory) để vẽ biểu đồ so sánh với Apriori. | 

## 2. Kế Hoạch Code Kiến Trúc 4 Tab Trên Streamlit (`app.py`)

Cấu trúc giao diện chuẩn giúp bạn dẫn dắt câu chuyện mượt mà không cần cuộn trang:

* **Sidebar (Thanh điều khiển bên trái):**

  * Nút chọn Dataset: *Toy Dataset (5-10 dòng để vẽ cây)* vs. *Real Dataset (Groceries \~10.000 dòng)*.

  * Các thanh trượt điều chỉnh tham số thời gian thực: `min_support` ($\text{min\_sup}$), `min_confidence` ($\text{min\_conf}$) và `min_lift`.

* **Tab 1 — Khám phá & Tiền xử lý dữ liệu (Data & Preprocessing):**

  * Hiển thị bảng giao dịch thô ban đầu (Raw Transactions).

  * Nút/Khối hiển thị ma trận nhị phân sau khi qua `TransactionEncoder` (One-Hot Encoding).

  * Biểu đồ cột (Bar Chart) thống kê Top 10 items xuất hiện nhiều nhất.

* **Tab 2 — Giải phẫu FP-Tree (White-Box Visualizer):**

  * Hiển thị bảng **Header Table (F-List)** đã lọc và sắp xếp giảm dần theo tần suất.

  * Render sơ đồ **Cây FP-Tree** trực tiếp bằng `st.graphviz_chart()` (áp dụng cho Toy Dataset) hoặc hiển thị **Tỷ lệ nén dữ liệu** (áp dụng cho Real Dataset).

  * Hộp chọn (Dropdown) 1 item bất kỳ ở cuối bảng Header Table để xuất ra các nhánh tiền tố (*Conditional Pattern Base*) và *Conditional FP-Tree* của item đó.

* **Tab 3 — Khai phá Luật & Hệ thống Gợi ý (Rules & Live Recommender):**

  * Hiển thị 2 bảng kết quả: `Frequent Itemsets` và `Association Rules` (hỗ trợ sort trực tiếp theo cột `Lift`).

  * **Live Recommender:** Tạo ô `st.multiselect("Giỏ hàng hiện tại:")`. Khi chọn thử món hàng $X$, code tự động lọc bảng luật có `antecedents == X` và hiện thẻ gợi ý mua kèm món hàng $Y$ kèm chỉ số `Confidence` và `Lift`.

* **Tab 4 — So găng Hiệu năng (FP-Growth vs. Apriori Benchmark):**

  * Nút bấm **"Chạy Benchmark"** cho $\text{min\_sup}$ chạy qua mảng `[0.1, 0.05, 0.02, 0.01]`.

  * Vẽ 2 biểu đồ đường (Line Chart) bằng `plotly` so sánh trực tiếp **Thời gian chạy (ms)** và **Bộ nhớ tiêu thụ (MB)** giữa FP-Growth và Apriori.

## 3. Lưu Ý Kỹ Thuật Quan Trọng Khi Code

1. **Sử dụng Sparse Matrix cho tập dữ liệu lớn:** Luôn bật tham số `sparse=True` trong `TransactionEncoder().transform(data, sparse=True)` để tránh tràn bộ nhớ RAM và đảm bảo tốc độ thực thi của FP-Growth.

2. **Giới hạn độ sâu khi vẽ cây bằng Graphviz:** Chỉ vẽ cây trực quan trên *Toy Dataset* (dưới 15 giao dịch) hoặc cắt lấy Top 10 items phổ biến nhất. Với tập dữ liệu hàng chục ngàn dòng, chỉ tính toán và in ra **con số tỷ lệ nén** (số lượng phần tử gốc vs. số nút trên cây) để tránh làm treo trình duyệt.

3. **Lưu bộ nhớ đệm bằng `@st.cache_data`:** Đặt decorator `@st.cache_data` của Streamlit lên trên hàm tiền xử lý dữ liệu và hàm chạy Benchmark với Apriori để kết quả được lưu sẵn, giúp chuyển Tab tức thì khi đang thuyết trình.