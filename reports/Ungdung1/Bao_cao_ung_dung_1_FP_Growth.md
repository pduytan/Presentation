# Ứng dụng FP Growth trong phân tích giỏ hàng bán lẻ
*G10  |  Ứng dụng 1  |  Nội dung cho slide 1*

Báo cáo sử dụng dữ liệu Online Retail để tìm những sản phẩm thường xuất hiện trong cùng hóa đơn, từ đó đề xuất thử nghiệm gợi ý mua kèm và phối hợp sản phẩm. Phạm vi phân tích là thị trường Anh trong giai đoạn 01/12/2010 đến 09/12/2011. Đây là minh họa khai phá dữ liệu lịch sử, không đại diện cho thị trường hiện nay. [1]

## Câu hỏi kinh doanh

Sản phẩm bán chạy cho biết từng mặt hàng phổ biến đến đâu. Người quản lý còn cần biết nhóm hàng nào được mua cùng nhau và mối liên hệ đó có mạnh hơn mức xuất hiện ngẫu nhiên theo tần suất riêng của từng mặt hàng hay không.

- Những tập sản phẩm nào xuất hiện cùng nhau trong ít nhất một tỷ lệ hóa đơn đã chọn?

- Khi hóa đơn có A, B xuất hiện với tỷ lệ bao nhiêu và cao hơn mức phổ biến chung của B đến mức nào?

- Những phát hiện nào đủ rõ để đề xuất thử một gợi ý mua kèm hoặc bộ sản phẩm?

![Hình 1. Vai trò của FP-Growth trong ứng dụng. Sơ đồ do tác giả xây dựng; cơ sở thuật toán [2], sinh luật [4].](../../outputs/Ungdung1/figures/05_so_do_ung_dung.png)
Hình 1. Vai trò của FP-Growth trong ứng dụng. Sơ đồ do tác giả xây dựng; cơ sở thuật toán [2], sinh luật [4].

## Kết quả chính

Phân tích giữ lại **17.901 hóa đơn** và **3.785 mã hàng**. Với minimum support 2%, độ dài tập mục tối đa 3, FP-Growth tìm được **414 tập mục**. Lọc tiếp confidence từ 60% và lift từ 1,5 thu được **36 luật có hướng**. Các con số là kết quả chạy lại trong nghiên cứu này, không phải số liệu được trích từ bài báo FP-Growth. [5]

Luật giữa hai mẫu bộ tách trà có 700 hóa đơn mua cùng, confidence 75,11% và lift 14,06. Kết quả tạo cơ sở chọn một giả thuyết kinh doanh để thử nghiệm; chưa chứng minh doanh thu hay lợi nhuận tăng. [5]

---

# Dữ liệu và đơn vị phân tích
*Nội dung cho slide 2*

Online Retail do Daqing Chen công bố trên UCI gồm 541.909 dòng và 8 trường trong tệp gốc. Một dòng mô tả một mặt hàng của hóa đơn; nhiều dòng có thể thuộc cùng một hóa đơn. Doanh nghiệp bán lẻ trực tuyến đăng ký tại Anh, chủ yếu bán quà tặng; nguồn dữ liệu cũng cho biết nhiều khách hàng là người mua sỉ. [1]

| Khái niệm | Cách xác định trong báo cáo |
| --- | --- |
| Một giao dịch | Một mã InvoiceNo sau lọc |
| Một item | Một StockCode hàng hóa hợp lệ |
| Sự hiện diện | Có hoặc không có mã hàng trong hóa đơn; không nhân trọng số theo Quantity |
| Quy mô sau lọc | 17.901 hóa đơn; 3.785 mã hàng; trung vị 15 mã hàng mỗi hóa đơn |

Giữ thị trường United Kingdom; loại hóa đơn hủy, dòng có Quantity hoặc UnitPrice không dương và mã ngoài quy ước hàng hóa đã chọn. Cùng một sản phẩm lặp trong hóa đơn chỉ tính hiện diện một lần. Không loại hóa đơn chỉ vì thiếu CustomerID, vì đơn vị phân tích là hóa đơn. Chi tiết định lượng nằm ở phụ lục nguồn và tái lập. [5]

**Kiểm tra dữ liệu gốc:** InvoiceNo và StockCode không thiếu. CustomerID thiếu 135.080 dòng (24,93%); vẫn có thể dùng hóa đơn để khai phá. Description thiếu 1.454 dòng; mã hàng được dùng làm khóa. [5]

![Hình 2. Tám sản phẩm có mặt trong nhiều hóa đơn nhất. Mẫu số là 17.901 hóa đơn; trục ngang đo tỷ lệ hiện diện, không đo số lượng bán hoặc doanh thu. Nguồn: tính từ [1], kết quả [5].](../../outputs/Ungdung1/figures/01_san_pham_pho_bien.png)
Hình 2. Tám sản phẩm có mặt trong nhiều hóa đơn nhất. Mẫu số là 17.901 hóa đơn; trục ngang đo tỷ lệ hiện diện, không đo số lượng bán hoặc doanh thu. Nguồn: tính từ [1], kết quả [5].

**Cách đọc:** mặt hàng phổ biến chưa chắc tạo ra luật mua kèm đáng chú ý. Cần xét quan hệ giữa các mặt hàng thay vì suy luận từ thứ hạng bán chạy.

---

# EDA về kích thước giỏ hàng và thời gian
*Nội dung cho slide 3*

EDA được thực hiện trên đúng 17.901 hóa đơn dùng để khai phá. Mục đích là xem giỏ hàng có lớn nhỏ khác nhau ra sao và dữ liệu phân bố theo thời gian như thế nào, trước khi đọc các mẫu mua cùng. [5]

![Hình 3. Phân bố kích thước giỏ và số hóa đơn hợp lệ theo tháng. Cột cam tháng 12/2011 chỉ gồm dữ liệu đến 09/12. N = 17.901; kích thước giỏ tính theo số mã hàng khác nhau. Nguồn: [5].](../../outputs/Ungdung1/figures/06_eda_gio_hang_va_thoi_gian.png)
Hình 3. Phân bố kích thước giỏ và số hóa đơn hợp lệ theo tháng. Cột cam tháng 12/2011 chỉ gồm dữ liệu đến 09/12. N = 17.901; kích thước giỏ tính theo số mã hàng khác nhau. Nguồn: [5].

**Kích thước giỏ:** trung vị 15, trung bình 26,46 và phân vị 95 là 77 mã hàng. Có 1.395 hóa đơn một sản phẩm (7,79%), vẫn được giữ để support dùng đúng mẫu số.

**Giỏ lớn:** 607 hóa đơn có hơn 100 mã hàng (3,39%); lớn nhất là 1.106 mã. Giữ các hóa đơn này trong phạm vi phân tích, đồng thời lưu ý quan hệ mua cùng có thể phản ánh hoạt động mua sỉ. Chưa tự động kết luận chúng là dữ liệu sai.

**Thời gian:** tháng 11/2011 có nhiều hóa đơn nhất (2.481). Tháng 12/2011 chưa đầy đủ, nên số hóa đơn thấp hơn không đủ để kết luận nhu cầu giảm. Phân tích toàn kỳ chưa kiểm soát yếu tố mùa vụ.

---

# Phương pháp và các chỉ số đánh giá
*Cơ sở đọc kết quả và hỗ trợ slide 4*

FP-Growth nén thông tin giao dịch vào FP-tree và khai phá qua các cây có điều kiện, tránh sinh tập ứng viên theo từng mức như Apriori. Trong ứng dụng này, đầu ra trực tiếp là tập mục thường xuyên; luật kết hợp được tạo ở bước tiếp theo. [2, 3]

Gọi N là số hóa đơn, n(X) là số hóa đơn chứa toàn bộ tập X. Với luật A → B, hai vế không giao nhau. Các chỉ số sử dụng trong báo cáo như sau. [4]

$$
\mathrm{support}(X)=\frac{n(X)}{N}
$$

**Support** đo mức phổ biến của một tập mục trong toàn bộ hóa đơn. Với luật A → B, support của luật là tỷ lệ hóa đơn chứa toàn bộ sản phẩm ở cả hai vế.

$$
\mathrm{confidence}(A\rightarrow B)=\frac{n(A\cup B)}{n(A)}
$$

**Confidence** là tỷ lệ hóa đơn có B trong số hóa đơn có A. Đổi chiều luật có thể làm confidence thay đổi.

$$
\mathrm{lift}(A\rightarrow B)=\frac{\mathrm{confidence}(A\rightarrow B)}{\mathrm{support}(B)}=\frac{N\,n(A\cup B)}{n(A)\,n(B)}
$$

**Lift** đối chiếu sự đồng xuất hiện với trường hợp độc lập: lớn hơn 1 là liên hệ dương trong mẫu; bằng 1 tương ứng mức độc lập; nhỏ hơn 1 là liên hệ âm. Lift không phải hệ số tăng doanh thu.

| Thiết lập | Giá trị | Ý nghĩa |
| --- | --- | --- |
| Minimum support | 2% | Ít nhất 359 trong 17.901 hóa đơn |
| Độ dài tập mục tối đa | 3 | Chỉ khai phá tập gồm 1 đến 3 sản phẩm |
| Minimum confidence | 60% | Lọc luật sau khi đã khai phá tập mục |
| Minimum lift | 1,5 | Loại luật có liên hệ yếu theo tiêu chí đang xét |

Các ngưỡng là lựa chọn phục vụ phân tích và khả năng diễn giải; không được khẳng định là tối ưu cho doanh nghiệp. Phần khảo sát ngưỡng giúp nhìn rõ ảnh hưởng của lựa chọn này. [5]

---

# Ảnh hưởng của minimum support
*Nội dung cho slide 4 về lựa chọn cấu hình*

Giữ nguyên dữ liệu, giới hạn độ dài tập mục là 3, confidence từ 60% và lift từ 1,5; chỉ thay minimum support. Khi ngưỡng giảm, số mẫu và số luật tăng mạnh. Các kết quả sau là số lượng khai phá được, không phải độ chính xác dự báo. [5]

| Minsup | Số HĐ tối thiểu | Tập mục | Luật sau lọc |
| --- | --- | --- | --- |
| 0,5% | 90 | 18.681 | 7.325 |
| 1,0% | 180 | 2.199 | 634 |
| 2,0% | 359 | 414 | 36 |
| 3,0% | 538 | 149 | 13 |
| 5,0% | 896 | 38 | 0 |

![Hình 4. Số tập mục và luật ở các ngưỡng 1%, 2%, 3%, 5%. Bảng phía trên còn cung cấp ngưỡng 0,5%. Nguồn: [5].](../../outputs/Ungdung1/figures/03_do_nhay_minsup.png)
Hình 4. Số tập mục và luật ở các ngưỡng 1%, 2%, 3%, 5%. Bảng phía trên còn cung cấp ngưỡng 0,5%. Nguồn: [5].

**Vì sao dùng 2% trong phần trình bày?** Ngưỡng này yêu cầu ít nhất 359 hóa đơn mua cùng, đồng thời cho 36 luật để xem xét. Đây là lựa chọn cân bằng quy mô bằng chứng và khối lượng kết quả cần đọc trong ví dụ này; chưa có tối ưu hóa lợi nhuận để xác nhận một ngưỡng kinh doanh tốt nhất.

**Vì sao 5% không còn luật?** Chỉ còn 38 tập đơn và không còn tập đôi đạt support 5%, nên không đủ tập mục nhiều sản phẩm để sinh luật. Điều đó không có nghĩa FP-Growth chạy sai.

Ngưỡng cao có thể bỏ qua các sản phẩm ngách; ngưỡng thấp có thể tạo quá nhiều luật và nhiều quan hệ khó sử dụng. Doanh nghiệp nên xét thêm số hóa đơn thực tế, biên lợi nhuận, tồn kho và khả năng hành động.

---

# Các mẫu mua cùng tiêu biểu
*Nội dung cho slide 5*

Tại cấu hình chính, 414 tập mục gồm 303 tập đơn, 106 tập đôi và 5 tập ba. Sau lọc có 36 luật có hướng, kể cả các luật có nhiều sản phẩm ở một vế. Ba luật dưới đây minh họa ba nhóm hàng; không phải danh sách ba luật có lift cao nhất. [5]

| Luật | Sản phẩm và mã hàng | Mua cùng | Support | Confidence | Lift |
| --- | --- | --- | --- | --- | --- |
| R1 | Túi hồng chấm bi → Túi đỏ Retrospot<br>22386 → 85099B | 785 | 4,39% | 67,73% | 6,27 |
| R2 | Bộ tách trà xanh → Bộ tách trà hoa hồng<br>22697 → 22699 | 700 | 3,91% | 75,11% | 14,06 |
| R3 | Đồng hồ xanh → Đồng hồ đỏ<br>22726 → 22727 | 563 | 3,15% | 64,27% | 12,37 |

![Hình 5. Tỷ lệ mua B khi có A so với mức phổ biến chung của B. N = 17.901; ánh xạ R1 đến R3 theo bảng trên. Nguồn: [5].](../../outputs/Ungdung1/figures/02_confidence_va_muc_nen.png)
Hình 5. Tỷ lệ mua B khi có A so với mức phổ biến chung của B. N = 17.901; ánh xạ R1 đến R3 theo bảng trên. Nguồn: [5].

**R1:** 785 hóa đơn chứa hai mẫu túi. B xuất hiện trong 10,81% tổng hóa đơn, nhưng trong 67,73% hóa đơn có A. Đây là cơ sở xem xét gợi ý phối hợp các mẫu túi.

**R2:** 700 hóa đơn chứa cả bộ tách trà xanh và bộ tách trà hoa hồng. Lift 14,06 cho thấy hai mẫu xuất hiện cùng nhau nhiều hơn rõ rệt so với mức kỳ vọng độc lập.

**R3:** 563 hóa đơn mua cùng hai màu đồng hồ. Mẫu này gợi ý khả năng người mua chọn nhiều biến thể cùng dòng; cần kiểm tra tiếp vai trò của khách mua sỉ trước khi thiết kế ưu đãi.

---

# Giải thích một luật từ các số đếm gốc
*Nội dung cho slide 6*

Xét R2 với A = GREEN REGENCY TEACUP AND SAUCER (22697), B = ROSES REGENCY TEACUP AND SAUCER (22699). Dưới đây là bảng đếm trực tiếp từ toàn bộ hóa đơn sau lọc; kết quả đã được đối chiếu với đầu ra FP-Growth. [5]

|  | Có B | Không có B | Tổng |
| --- | --- | --- | --- |
| Có A | 700 | 232 | 932 |
| Không có A | 256 | 16.713 | 16.969 |
| Tổng | 956 | 16.945 | 17.901 |

$$
\mathrm{support}(A\cup B)=\frac{700}{17901}\approx 3.91\%
$$

Có 700 trong 17.901 hóa đơn chứa cả hai mẫu tách trà. Support 3,91% được tính trên toàn bộ hóa đơn, không chỉ trên hóa đơn mua tách trà.

$$
\mathrm{confidence}(A\rightarrow B)=\frac{700}{932}\approx 75.11\%
$$

Trong 932 hóa đơn có A, 700 hóa đơn cũng có B. Đây là ý nghĩa cụ thể của confidence 75,11%; chưa phải xác suất một khách hàng mới sẽ chấp nhận gợi ý.

$$
\mathrm{lift}(A\rightarrow B)=\frac{700/932}{956/17901}\approx 14.06
$$

B vốn có mặt trong 5,34% tổng hóa đơn. Nếu sự hiện diện của A và B độc lập với các tần suất biên đang quan sát, số hóa đơn mua cùng kỳ vọng là khoảng 49,8. Thực tế có 700, tương ứng lift 14,06.

**Đổi chiều:** confidence B → A = 700/956 = 73,22%. Hai chiều có cùng support và lift, nhưng confidence khác nhau. Vì vậy hệ thống gợi ý cần xét rõ sản phẩm đang có trong giỏ và sản phẩm được đề xuất.

---

# Từ phát hiện dữ liệu đến quyết định kinh doanh
*Nội dung cho slide 7*

Các luật tạo ra danh sách quan hệ cần xem xét. Quyết định triển khai còn phụ thuộc giá bán, biên lợi nhuận, tồn kho, đặc điểm người mua và mức độ phù hợp của sản phẩm. Các phương án dưới đây là đề xuất thử nghiệm dựa trên phát hiện; chưa được đánh giá bằng thử nghiệm bán hàng.

## Gợi ý một mẫu túi khác khi đã có túi trong giỏ

R1 có 785 hóa đơn mua cùng và confidence 67,73%. Có thể thử hiển thị mẫu túi đỏ khi giỏ có mẫu hồng chấm bi, với điều kiện mẫu đỏ chưa có trong giỏ và còn hàng. Cần kiểm tra đây là nhu cầu phối mẫu hay đặc điểm đặt hàng số lượng lớn.

## Giới thiệu bộ phối hợp các mẫu tách trà

R2 có support 3,91% và lift 14,06. Có thể thử một trang bộ sưu tập gồm mẫu xanh và mẫu hoa hồng, kèm lựa chọn mua từng mẫu. Dữ liệu chưa đủ để xác định có cần giảm giá hay giảm bao nhiêu.

## Trưng bày nhiều màu của cùng dòng đồng hồ

R3 ghi nhận 563 hóa đơn mua cùng hai màu. Có thể thử liên kết các biến thể trên trang sản phẩm. Vì nhiều khách trong dữ liệu là người mua sỉ [1], không suy diễn rằng mọi người mua lẻ đều có nhu cầu sở hữu nhiều đồng hồ.

## Đánh giá bằng thử nghiệm có nhóm đối chứng

Trong một thử nghiệm A/B, phân bổ ngẫu nhiên khách hàng hoặc phiên truy cập đủ điều kiện vào nhóm có và không có gợi ý. Quy định trước sản phẩm, quy tắc gợi ý, thời gian và thước đo. Có thể theo dõi tỷ lệ thêm sản phẩm được gợi ý, tỷ lệ hoàn tất đơn và lợi nhuận đóng góp trên mỗi đơn, đồng thời theo dõi hủy hoặc trả hàng.

Chưa có số liệu giá vốn và thử nghiệm can thiệp trong phân tích này, vì vậy không đưa ra con số tăng doanh thu hay lợi nhuận. Một luật có lift cao chỉ cho thấy quan hệ đồng xuất hiện mạnh theo mẫu số đã xác định.

## Kết luận trình bày

FP-Growth giúp chuyển 17.901 hóa đơn thành những tập mua cùng có thể giải thích bằng số đếm. Kết hợp support, confidence và lift giúp chọn quan hệ đáng xem xét hơn việc chỉ nhìn mặt hàng phổ biến. Giá trị kinh doanh cần được kiểm chứng bằng một hành động cụ thể và phép đo phù hợp.

---

# Đối chiếu trên giai đoạn đến sau
*Phụ lục kiểm tra kết quả theo thời gian*

Để kiểm tra mức ổn định theo thời gian, một lần phân tích riêng chỉ khai phá luật trên 12.887 hóa đơn trước 01/10/2011. Sau đó giữ cố định ba luật đơn có support cao nhất từ giai đoạn này, bỏ cặp đảo chiều, rồi đếm lại trên 5.014 hóa đơn từ 01/10 đến 09/12/2011. Không dùng giai đoạn sau để xây cây hoặc chọn các luật trong lần đối chiếu này. [5]

![Hình 6. Confidence trước và sau mốc 01/10/2011. T1 = 22386 → 85099B; T2 = 22697 → 22699; T3 = 21931 → 85099B. T3 khác R3 của bảng minh họa toàn kỳ. Nguồn: [5].](../../outputs/Ungdung1/figures/04_doi_chieu_thoi_gian.png)
Hình 6. Confidence trước và sau mốc 01/10/2011. T1 = 22386 → 85099B; T2 = 22697 → 22699; T3 = 21931 → 85099B. T3 khác R3 của bảng minh họa toàn kỳ. Nguồn: [5].

| Luật | HĐ mua cùng ở kỳ sau | Support kỳ sau | Confidence kỳ sau | Lift kỳ sau |
| --- | --- | --- | --- | --- |
| T1 | 156 | 3,11% | 67,83% | 7,59 |
| T2 | 140 | 2,79% | 76,92% | 19,68 |
| T3 | 144 | 2,87% | 65,45% | 7,33 |

Với luật bộ tách trà T2, confidence từ 74,67% ở kỳ trước lên 76,92% ở kỳ sau. Kỳ sau có 182 hóa đơn chứa A, trong đó 140 cũng có B. Cả ba luật được kiểm tra vẫn có confidence trên 60% và lift trên 1,5.

**Ý nghĩa:** ba quan hệ được chọn còn xuất hiện ở giai đoạn đến sau trong cùng bộ dữ liệu. Đối chiếu này hỗ trợ nhận xét về độ ổn định quan sát được, chưa đo khả năng làm tăng tỷ lệ mua khi triển khai gợi ý.

**Giới hạn:** kỳ sau chứa mùa cuối năm và chỉ đến ngày 09/12; không phải một quý đầy đủ. Dữ liệu đến từ cùng doanh nghiệp và thuộc năm 2010–2011, nên cần đánh giá lại khi thay thị trường hoặc thời điểm.

---

# Khung chuyển thành bảy slide
*Tổng thời lượng mục tiêu 7 phút*

Mỗi slide nên giữ một thông điệp và một hình hoặc bảng chính. Các lời nói dưới đây là ý dẫn; luyện diễn giải theo cách hiểu của người trình bày, chỉ vào các con số trên hình và dành thời gian giải thích kết quả.

## Slide 1  Bài toán kinh doanh  40 giây

**Tư liệu:** Hình 1; trang 1. Cửa hàng biết sản phẩm nào bán chạy nhưng còn cần biết các sản phẩm nào thường nằm trong cùng hóa đơn. Phần này dùng FP-Growth để tìm các nhóm mua cùng và xem chúng có thể hỗ trợ gợi ý mua kèm như thế nào.

## Slide 2  Dữ liệu và giao dịch  50 giây

**Tư liệu:** Hình 2; trang 2. Một dòng dữ liệu là một mặt hàng của hóa đơn, còn giao dịch dùng cho thuật toán là toàn bộ hóa đơn. Sau khi giới hạn thị trường Anh và lọc dữ liệu, tập phân tích có 17.901 hóa đơn và 3.785 mã hàng. Số lần mua nhiều đơn vị không được nhân vào support.

## Slide 3  EDA và đặc điểm giỏ hàng  55 giây

**Tư liệu:** Hình 3; trang 3. Giỏ hàng có trung vị 15 mã sản phẩm nhưng trung bình 26,46 mã, cho thấy phân bố lệch về phía giỏ lớn. Có 607 hóa đơn trên 100 mã, phù hợp với việc nguồn dữ liệu có khách mua sỉ. Tháng 11 có nhiều hóa đơn nhất; tháng 12 chỉ đến ngày 9 nên không thể so như một tháng đầy đủ.

## Slide 4  Khảo sát và chọn cấu hình  60 giây

**Tư liệu:** Hình 4 và bảng ngưỡng; trang 5. Nhóm thử nhiều mức support trên cùng dữ liệu. Từ 1% lên 2%, số luật giảm từ 634 xuống 36, giúp tập trung vào các quan hệ có ít nhất 359 hóa đơn mua cùng. Cấu hình chính giới hạn tập mục dài tối đa 3, confidence từ 60% và lift từ 1,5. Đây là ngưỡng phục vụ phân tích, chưa phải tối ưu lợi nhuận.

## Slide 5  Ba kết quả tiêu biểu  70 giây

**Tư liệu:** Bảng R1 đến R3 và Hình 5; trang 6. Tại support 2% và giới hạn ba sản phẩm, ta thu được 414 tập mục và 36 luật đạt ngưỡng. Ba ví dụ thuộc nhóm túi, tách trà và đồng hồ. Biểu đồ đối chiếu tỷ lệ B trong hóa đơn có A với tỷ lệ B trên toàn bộ hóa đơn, giúp thấy rõ mức liên hệ của từng cặp.

## Slide 6  Giải thích luật bộ tách trà  75 giây

**Tư liệu:** Bảng số đếm và công thức thay số; trang 7. Có 932 hóa đơn mua mẫu xanh, 956 hóa đơn mua mẫu hoa hồng và 700 hóa đơn mua cả hai. Do đó support là 3,91%, confidence 75,11% và lift 14,06. Lift không có nghĩa doanh thu tăng 14 lần; nó so sánh số lần đồng xuất hiện với kỳ vọng độc lập.

## Slide 7  Đề xuất kinh doanh và giới hạn  70 giây

**Tư liệu:** Trang 8. Từ dữ liệu có thể đề xuất thử gợi ý các mẫu túi, phối bộ tách trà hoặc liên kết các màu đồng hồ. Cần thử nghiệm với nhóm đối chứng và theo dõi cả lợi nhuận, không chỉ lượt nhấp. Kết luận là FP-Growth cung cấp quan hệ có bằng chứng để thử nghiệm, chứ bản thân thuật toán chưa tạo ra lợi nhuận.

Nếu cần rút xuống 6 phút, rút gọn phần dữ liệu, EDA và đọc bảng kết quả; vẫn giữ giải thích một luật bằng số đếm. Đối chiếu theo thời gian ở trang 9 là phần dự phòng. Demo do thành viên 5 và 6 phối hợp thực hiện, dùng dữ liệu và cấu hình thống nhất với phần phân tích này.

---

# Câu hỏi phản biện và cách trả lời
*Phụ lục học và bảo vệ phần ứng dụng*

## Ứng dụng này thực sự dùng FP-Growth ở đâu

Thuật toán nhận các tập mã sản phẩm của từng hóa đơn và tìm tập mục đạt minimum support. Bảng luật và gợi ý mua kèm được xây từ đầu ra đó. Chạy thống kê cặp đơn thuần mà không thực hiện khai phá tập mục thì chưa minh họa đúng vai trò FP-Growth.

## Vì sao dùng FP-Growth thay vì Apriori

FP-Growth khai phá trên cấu trúc FP-tree và các bài toán có điều kiện, tránh sinh ứng viên theo từng mức [2]. Báo cáo này không đo thời gian hai thuật toán, nên không khẳng định nhanh hơn bao nhiêu lần trên bộ dữ liệu đang xét.

## Có tìm được tất cả tập mục thường xuyên không

Cấu hình đã giới hạn max_len = 3, nên 414 là toàn bộ tập mục đạt ngưỡng trong phạm vi độ dài 1 đến 3. Không khẳng định đã liệt kê các tập dài hơn. Giới hạn giúp tập trung vào những nhóm nhỏ dễ trình bày.

## Vì sao vẫn giữ hóa đơn chỉ có một sản phẩm

Đó vẫn là giao dịch hợp lệ trong tổng thể đang phân tích. Loại chúng sẽ đổi mẫu số support và thay đổi ý nghĩa tỷ lệ; vì vậy vẫn giữ cả hóa đơn không chứa bất kỳ item nào đạt ngưỡng lọc tần suất.

## Confidence cao có đủ để chọn luật không

Chưa đủ. Nếu B vốn xuất hiện rất thường xuyên thì confidence có thể cao dù A cung cấp ít thông tin bổ sung. Cần đọc cùng support, số hóa đơn thực tế và lift; sau đó xem tính phù hợp về kinh doanh.

## Lift 14 có nghĩa gợi ý sẽ làm khách mua nhiều gấp 14 lần không

Không. Nó so sánh mức đồng xuất hiện quan sát với kỳ vọng độc lập từ tần suất biên. Dữ liệu hóa đơn có thể chịu ảnh hưởng của mua sỉ, bộ sưu tập, mùa vụ hoặc yếu tố chưa đo; cần thử nghiệm can thiệp để kết luận tác động.

## Vì sao không xóa các dòng thiếu CustomerID

Câu hỏi hiện tại là đồng xuất hiện theo hóa đơn, và InvoiceNo đã xác định giỏ hàng. Xóa chỉ vì thiếu CustomerID sẽ làm mất những giao dịch vẫn sử dụng được. Nếu chuyển sang cá nhân hóa theo người mua thì phải thiết kế lại dữ liệu và phạm vi.

## Làm sao biết số liệu báo cáo có thể kiểm chứng

Mã nguồn đọc tệp UCI, lưu bảng số đếm, tập mục, luật và khảo sát ngưỡng. Các luật minh họa được đếm lại trực tiếp từ giỏ hàng rồi so sánh với kết quả thư viện. Tệp thống kê ghi phiên bản thư viện và mã SHA-256 của dữ liệu gốc. [5]

---

# Nguồn tham khảo và thông tin tái lập
*Phụ lục kiểm chứng*

## [1] Dữ liệu

Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository. DOI 10.24432/C5BW33. Giấy phép CC BY 4.0.

[Mở nguồn](https://archive.ics.uci.edu/dataset/352/online+retail)

## [2] Cơ sở thuật toán

Han, J., Pei, J., Yin, Y., & Mao, R. (2004). Mining Frequent Patterns without Candidate Generation: A Frequent-Pattern Tree Approach. Data Mining and Knowledge Discovery, 8, 53–87. Mục 2 về FP-tree; mục 3 về khai phá.

[Mở nguồn](https://www.cs.sfu.ca/~jpei/publications/dami03_fpgrowth.pdf)

## [3] Cài đặt FP-Growth

Raschka và cộng sự. mlxtend user guide: fpgrowth. Hướng dẫn hàm khai phá frequent itemsets.

[Mở nguồn](https://rasbt.github.io/mlxtend/user_guide/frequent_patterns/fpgrowth/)

## [4] Định nghĩa chỉ số

Raschka và cộng sự. mlxtend user guide: association_rules. Công thức support, confidence và lift.

[Mở nguồn](https://rasbt.github.io/mlxtend/user_guide/frequent_patterns/association_rules/)

## [5] Kết quả tự tính

FP-Growth chạy ngày 03/11/2026: analysis.py, results/stats.json và các bảng tập mục, luật, ngưỡng. EDA bổ sung ngày 05/11/2026: eda_business.py, results/eda_stats.json. Biểu đồ số liệu được tạo từ các tệp kết quả đi kèm.

## Các bước lọc và số dòng còn lại

| Bước | Số dòng |
| --- | --- |
| Dữ liệu gốc toàn bộ quốc gia | 541.909 |
| Chỉ thị trường United Kingdom | 495.478 |
| Loại hóa đơn hủy | 487.622 |
| Giữ số lượng dương | 486.286 |
| Giữ đơn giá dương | 485.123 |
| Giữ mã hàng hóa năm chữ số và tối đa hai chữ cái | 483.971 |
| Một lần hiện diện cho mỗi sản phẩm trong mỗi hóa đơn | 473.691 |

Quy ước mã hàng: 5 chữ số và tối đa 2 chữ cái. Phiên bản: Python 3.12.14; pandas 3.0.1; NumPy 2.3.5; mlxtend 0.25.0. Giữ toàn bộ hóa đơn khi lọc item theo tần suất; tên hiển thị lấy mô tả phổ biến nhất của mã. SHA-256 của dữ liệu nằm trong results/stats.json. Ngày truy cập và tính toán: 03/11/2026.

---
