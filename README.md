# Dự án Khai phá Tập phổ biến & Luật kết hợp (FP-Growth / Apriori) — CS313

Dự án được tổ chức theo cấu trúc chuẩn của một dự án Khoa học Dữ liệu (Data Science Project), tách biệt rõ ràng giữa **Dữ liệu (`data/`)**, **Mã nguồn (`src/`)**, **Kết quả đầu ra (`outputs/`)** và **Báo cáo & Slide (`reports/`)**.

## Cấu trúc Cây thư mục

```text
Presentation/
├── data/                                           # Dữ liệu gốc dùng chung (không trùng lặp)
│   ├── Online Retail.xlsx                          # Dữ liệu Ứng dụng 1 (UCI Online Retail)
│   └── mimic-iv-clinical-database-demo-2.2/        # Dữ liệu Ứng dụng 3 (MIMIC-IV Clinical Database Demo)
│       ├── hosp/
│       └── icu/
│
├── src/                                            # Mã nguồn xử lý của 3 ứng dụng
│   ├── Ungdung1/                                   # Ứng dụng 1: Phân tích Giỏ hàng Bán lẻ (Online Retail)
│   │   ├── analysis.py                             # Khai phá tập phổ biến & luật kết hợp bằng FP-Growth
│   │   ├── eda_business.py                         # Phân tích khám phá dữ liệu (EDA) giỏ hàng & thời gian
│   │   ├── make_figures.py                         # Sinh bộ biểu đồ PNG/SVG phục vụ báo cáo & slide
│   │   └── build_report.py                         # Tạo báo cáo Markdown và xuất PDF tự động
│   ├── Ungdung2/                                   # Ứng dụng 2 (Đang phát triển)
│   └── Ungdung3/                                   # Ứng dụng 3: Phân tích Bệnh đồng mắc (MIMIC-IV)
│       └── Comorbidity.py                          # Khai phá bệnh đồng mắc & so sánh Apriori vs FP-Growth
│
├── outputs/                                        # Kết quả thực nghiệm & hình ảnh trực quan hóa
│   ├── Ungdung1/
│   │   ├── figures/                                # Các biểu đồ (.png, .svg) và công thức của Ứng dụng 1
│   │   └── results/                                # Các file thống kê (.json) và bảng kết quả (.csv)
│   ├── Ungdung2/
│   └── Ungdung3/
│       └── comorbidity_rules.csv                   # Bảng luật kết hợp bệnh đồng mắc xuất từ Ứng dụng 3
│
├── reports/                                        # Tài liệu báo cáo và nội dung thuyết trình
│   ├── Ungdung1/
│   │   ├── Bao_cao_ung_dung_1_FP_Growth.pdf        # Bản báo cáo PDF hoàn chỉnh (12 trang)
│   │   ├── Bao_cao_ung_dung_1_FP_Growth.md         # Bản báo cáo Markdown có thể chỉnh sửa
│   │   ├── Noi_dung_7_slide_Ung_dung_1.md          # Dàn ý và lời thuyết trình cho 7 slide
│   │   └── README.md                               # Ghi chú tái lập thực nghiệm của Ứng dụng 1
│   ├── Ungdung2/
│   └── Ungdung3/
│
├── demo.py                                         # Giao diện Web (Streamlit) tích hợp cả 3 ứng dụng
├── requirements.txt                                # Danh sách thư viện cần cài đặt
└── README.md                                       # Tài liệu hướng dẫn tổng quan dự án
```

## Hướng dẫn Chạy Nhanh

### 1. Cài đặt thư viện
```powershell
python -m pip install -r requirements.txt
```

### 2. Chạy Giao diện Demo Tổng hợp (Streamlit)
```powershell
streamlit run demo.py
```

### 3. Chạy độc lập từng Ứng dụng từ dòng lệnh
- **Ứng dụng 1 (Giỏ hàng Bán lẻ - Online Retail):**
  ```powershell
  python src/Ungdung1/analysis.py
  python src/Ungdung1/eda_business.py
  python src/Ungdung1/make_figures.py
  python src/Ungdung1/build_report.py
  ```
- **Ứng dụng 3 (Bệnh đồng mắc - MIMIC-IV):**
  ```powershell
  python src/Ungdung3/Comorbidity.py
  ```
