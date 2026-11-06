# Ứng dụng FP Growth trong phân tích giỏ hàng bán lẻ

Bộ tài liệu cho phần Ứng dụng 1 của G10. Báo cáo cập nhật ngày 05/11/2026 có 12 trang và khung chuyển thành 7 slide trong khoảng 7 phút. Mạch phân tích là chọn dữ liệu, EDA, khảo sát cấu hình, chạy FP-Growth, diễn giải kết quả và đưa nội dung vào slide. Các số liệu được tính từ tệp Online Retail gốc của UCI, không phải số minh họa tự đặt.

## Tệp sử dụng (Theo cấu trúc thư mục chuẩn của dự án)

- `reports/Ungdung1/Bao_cao_ung_dung_1_FP_Growth.pdf`: bản đọc và chia sẻ.
- `reports/Ungdung1/Bao_cao_ung_dung_1_FP_Growth.md`: bản nội dung có thể chỉnh sửa, chứa công thức LaTeX và liên kết hình.
- `reports/Ungdung1/Noi_dung_7_slide_Ung_dung_1.md`: nội dung gạch đầu dòng và lời nói theo từng slide, dành cho người dựng slide.
- `outputs/Ungdung1/figures/`: 4 biểu đồ số liệu chính, hình EDA hai biểu đồ, 1 sơ đồ quy trình và ảnh công thức; PNG dùng trực tiếp trong slide, SVG của các biểu đồ dùng khi cần đồ họa vector.
- `outputs/Ungdung1/results/`: bảng số liệu, tập mục, luật, khảo sát ngưỡng và thống kê có phiên bản thư viện.
- `src/Ungdung1/analysis.py`: mã phân tích và kiểm tra số đếm.
- `src/Ungdung1/eda_business.py`: EDA về thiếu dữ liệu, kích thước giỏ hàng và số hóa đơn theo tháng.
- `src/Ungdung1/make_figures.py`: tạo các biểu đồ từ kết quả phân tích.
- `src/Ungdung1/build_report.py`: tạo nội dung Markdown và báo cáo PDF.
- `data/Online Retail.xlsx`: dữ liệu gốc được giữ nguyên tại thư mục dữ liệu dùng chung.

## Dữ liệu và nguồn

Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository. DOI: https://doi.org/10.24432/C5BW33. Giấy phép CC BY 4.0.

Trang nguồn: https://archive.ics.uci.edu/dataset/352/online+retail

Tải gốc: https://archive.ics.uci.edu/static/public/352/online+retail.zip

SHA-256 của `Online Retail.xlsx`:

`43465a06f2ccf7c8b5bd2892bc7defb52f97487934fe93b16ae4c3936424676d`

Nguồn thuật toán và công thức nằm trong báo cáo, trang 12. Các kết quả 17.901 hóa đơn, 414 tập mục và 36 luật là phân tích trong bộ tài liệu này, không phải kết quả xuất bản của UCI hoặc Han và cộng sự.

## Tái lập

Trong môi trường Python 3.12, cài các gói trong `requirements.txt`, sau đó chạy theo thứ tự:

```powershell
python -m pip install -r requirements.txt
python src/Ungdung1/analysis.py
python src/Ungdung1/eda_business.py
python src/Ungdung1/make_figures.py
python src/Ungdung1/build_report.py
```

Có thể chạy từ thư mục gốc của dự án hoặc từ bất kỳ đâu (đường dẫn đã được chuẩn hóa tự động theo cây thư mục dự án). Bản dựng hình và PDF sử dụng Arial tại `C:/Windows/Fonts`; nếu chạy hệ điều hành khác, sửa đường dẫn font trong hai tệp tạo hình và tạo báo cáo.

`analysis.py` giữ tất cả hóa đơn hợp lệ trong mẫu số, kể cả sau khi bỏ item hiếm. Tập mục giới hạn tối đa 3 sản phẩm. Khảo sát các mức support 0,5%, 1%, 2%, 3% và 5%; lọc luật với confidence ít nhất 60% và lift ít nhất 1,5.

Trong đối chiếu theo thời gian, luật được khai phá trên hóa đơn trước 01/10/2011 và đánh giá lại trên hóa đơn đến sau. Hai tập không có hóa đơn giao nhau. Danh sách item sơ tuyển ở ngưỡng 0,5% toàn kỳ vẫn chứa mọi item đạt 2% tập trước, vì 0,02 × 12.887 lớn hơn 0,005 × 17.901; bước sơ tuyển vì vậy không làm mất item thường xuyên của lần kiểm tra này.

## Dùng cho slide

Trang 10 của báo cáo nêu thứ tự, thời lượng và lời nói gợi ý cho 7 slide. Trang 3 là EDA bổ sung; trang 5 khảo sát cấu hình; trang 11 là câu hỏi phản biện. Đối chiếu theo thời gian ở trang 9 là phân tích dự phòng. Kết quả là quan hệ đồng xuất hiện theo hóa đơn; không diễn giải lift thành mức tăng doanh thu hay hiệu quả nhân quả.

Người phụ trách ứng dụng 1 cung cấp dữ liệu, EDA, cấu hình và kết quả đã diễn giải. Thành viên 5 và 6 phối hợp làm demo và tổng hợp slide, giữ cùng phạm vi dữ liệu và cấu hình để các con số khớp nhau.
