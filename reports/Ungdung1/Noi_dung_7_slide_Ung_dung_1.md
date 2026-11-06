# Nội dung đưa vào slide ứng dụng 1

Mạch trình bày: bài toán → dữ liệu → EDA → cấu hình → kết quả → diễn giải → kết luận. Tổng thời lượng khoảng 7 phút.

## Slide 1  Bài toán kinh doanh
Thời lượng: 40 giây.

- Tìm nhóm sản phẩm thường xuất hiện trong cùng hóa đơn.
- Dùng kết quả để đề xuất thử gợi ý mua kèm.
- Dữ liệu Online Retail giai đoạn 2010–2011.

Hình hoặc bảng: Hình 1; trang 1.

Lời trình bày gợi ý: Cửa hàng biết sản phẩm nào bán chạy nhưng còn cần biết các sản phẩm nào thường nằm trong cùng hóa đơn. Phần này dùng FP-Growth để tìm các nhóm mua cùng và xem chúng có thể hỗ trợ gợi ý mua kèm như thế nào.

## Slide 2  Dữ liệu và giao dịch
Thời lượng: 50 giây.

- Dữ liệu gốc: 541.909 dòng và 8 trường.
- Phạm vi sau lọc: 17.901 hóa đơn, 3.785 mã hàng.
- Một InvoiceNo là một giỏ hàng; mỗi StockCode chỉ tính hiện diện một lần.

Hình hoặc bảng: Hình 2; trang 2.

Lời trình bày gợi ý: Một dòng dữ liệu là một mặt hàng của hóa đơn, còn giao dịch dùng cho thuật toán là toàn bộ hóa đơn. Sau khi giới hạn thị trường Anh và lọc dữ liệu, tập phân tích có 17.901 hóa đơn và 3.785 mã hàng. Số lần mua nhiều đơn vị không được nhân vào support.

## Slide 3  EDA và đặc điểm giỏ hàng
Thời lượng: 55 giây.

- Trung vị 15 mã hàng/giỏ, trung bình 26,46.
- 607 giỏ trên 100 mã (3,39%): lưu ý ảnh hưởng mua sỉ.
- Tháng 11/2011 cao nhất: 2.481 hóa đơn; tháng 12 chỉ đến ngày 9.

Hình hoặc bảng: Hình 3; trang 3.

Lời trình bày gợi ý: Giỏ hàng có trung vị 15 mã sản phẩm nhưng trung bình 26,46 mã, cho thấy phân bố lệch về phía giỏ lớn. Có 607 hóa đơn trên 100 mã, phù hợp với việc nguồn dữ liệu có khách mua sỉ. Tháng 11 có nhiều hóa đơn nhất; tháng 12 chỉ đến ngày 9 nên không thể so như một tháng đầy đủ.

## Slide 4  Khảo sát và chọn cấu hình
Thời lượng: 60 giây.

- Minsup 2% tương ứng ít nhất 359 hóa đơn.
- Max_len = 3; confidence từ 60%; lift từ 1,5.
- Khảo sát 1% cho 634 luật, 2% cho 36 luật; chọn 2% để tập trung diễn giải.

Hình hoặc bảng: Hình 4 và bảng ngưỡng; trang 5.

Lời trình bày gợi ý: Nhóm thử nhiều mức support trên cùng dữ liệu. Từ 1% lên 2%, số luật giảm từ 634 xuống 36, giúp tập trung vào các quan hệ có ít nhất 359 hóa đơn mua cùng. Cấu hình chính giới hạn tập mục dài tối đa 3, confidence từ 60% và lift từ 1,5. Đây là ngưỡng phục vụ phân tích, chưa phải tối ưu lợi nhuận.

## Slide 5  Ba kết quả tiêu biểu
Thời lượng: 70 giây.

- 414 tập mục: 303 tập đơn, 106 tập đôi, 5 tập ba.
- 36 luật có hướng đạt cấu hình đã chọn.
- Ba ví dụ: túi hồng → túi đỏ; tách xanh → tách hoa hồng; đồng hồ xanh → đồng hồ đỏ.

Hình hoặc bảng: Bảng R1 đến R3 và Hình 5; trang 6.

Lời trình bày gợi ý: Tại support 2% và giới hạn ba sản phẩm, ta thu được 414 tập mục và 36 luật đạt ngưỡng. Ba ví dụ thuộc nhóm túi, tách trà và đồng hồ. Biểu đồ đối chiếu tỷ lệ B trong hóa đơn có A với tỷ lệ B trên toàn bộ hóa đơn, giúp thấy rõ mức liên hệ của từng cặp.

## Slide 6  Giải thích luật bộ tách trà
Thời lượng: 75 giây.

- A = tách xanh: 932 hóa đơn; B = tách hoa hồng: 956 hóa đơn; cùng A và B: 700.
- Support = 700/17.901 ≈ 3,91%; confidence = 700/932 ≈ 75,11%.
- Lift ≈ 14,06: quan hệ đồng xuất hiện mạnh so với mức độc lập.

Hình hoặc bảng: Bảng số đếm và công thức thay số; trang 7.

Lời trình bày gợi ý: Có 932 hóa đơn mua mẫu xanh, 956 hóa đơn mua mẫu hoa hồng và 700 hóa đơn mua cả hai. Do đó support là 3,91%, confidence 75,11% và lift 14,06. Lift không có nghĩa doanh thu tăng 14 lần; nó so sánh số lần đồng xuất hiện với kỳ vọng độc lập.

## Slide 7  Đề xuất kinh doanh và giới hạn
Thời lượng: 70 giây.

- Đề xuất thử gợi ý mua kèm hoặc giới thiệu bộ sưu tập.
- Xem xét tồn kho, giá và biên lợi nhuận trước khi triển khai.
- Kiểm chứng hiệu quả bằng thử nghiệm; dữ liệu mua cùng chưa chứng minh tăng doanh thu.

Hình hoặc bảng: Trang 8.

Lời trình bày gợi ý: Từ dữ liệu có thể đề xuất thử gợi ý các mẫu túi, phối bộ tách trà hoặc liên kết các màu đồng hồ. Cần thử nghiệm với nhóm đối chứng và theo dõi cả lợi nhuận, không chỉ lượt nhấp. Kết luận là FP-Growth cung cấp quan hệ có bằng chứng để thử nghiệm, chứ bản thân thuật toán chưa tạo ra lợi nhuận.

## Phối hợp với thành viên 5 và 6

Người phụ trách ứng dụng 1 bàn giao dữ liệu, EDA, cấu hình, kết quả và cách diễn giải. Thành viên 5 và 6 phụ trách phối hợp demo và dựng slide từ các nội dung này. Giữ cấu hình và phạm vi dữ liệu thống nhất để số liệu khớp báo cáo.

Nguồn và kết quả tái lập: xem trang 12 của báo cáo và README.md.