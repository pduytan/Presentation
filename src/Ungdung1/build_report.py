"""Build a slide-aligned Vietnamese report and its editable Markdown source."""
from pathlib import Path
import sys,json,html,math,textwrap
ROOT=Path(__file__).resolve().parent
PROJECT_ROOT=ROOT.parents[1]
RESULT_DIR=PROJECT_ROOT/'outputs'/'Ungdung1'/'results'
FIG_DIR=PROJECT_ROOT/'outputs'/'Ungdung1'/'figures'
REPORT_DIR=PROJECT_ROOT/'reports'/'Ungdung1'
FIG_DIR.mkdir(parents=True,exist_ok=True)
REPORT_DIR.mkdir(parents=True,exist_ok=True)
vendor=PROJECT_ROOT/'tmp'/'fpgrowth_vendor'
if vendor.exists():sys.path.insert(0,str(vendor))
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT,TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

S=json.loads((RESULT_DIR/'stats.json').read_text(encoding='utf-8'))
E=json.loads((RESULT_DIR/'eda_stats.json').read_text(encoding='utf-8'))
N=S['n_baskets'];R=S['report_rules'];DEEP=R[1]
def num(x):return f'{int(x):,}'.replace(',','.')
def pct(x,d=2):return f'{100*x:.{d}f}%'.replace('.',',')
def dec(x,d=2):return f'{x:.{d}f}'.replace('.',',')

# Numerical substitutions are rendered at high resolution for direct slide reuse.
subst={
 'support_example':rf'\mathrm{{support}}(A\cup B)=\frac{{{DEEP["n_ab"]}}}{{{N}}}\approx {100*DEEP["support"]:.2f}\%',
 'confidence_example':rf'\mathrm{{confidence}}(A\rightarrow B)=\frac{{{DEEP["n_ab"]}}}{{{DEEP["n_a"]}}}\approx {100*DEEP["confidence"]:.2f}\%',
 'lift_example':rf'\mathrm{{lift}}(A\rightarrow B)=\frac{{{DEEP["n_ab"]}/{DEEP["n_a"]}}}{{{DEEP["n_b"]}/{N}}}\approx {DEEP["lift"]:.2f}',
}
for name,tex in subst.items():
 fig=plt.figure(figsize=(9,.65));fig.text(.5,.5,f'${tex}$',ha='center',va='center',fontsize=19)
 fig.savefig(FIG_DIR/f'formula_{name}.png',dpi=260,bbox_inches='tight',pad_inches=.14)
 plt.close(fig)

PAGES=[]
def page(title,tag,blocks):PAGES.append({'title':title,'tag':tag,'blocks':blocks})
def p(text):return ('p',text)
def sub(text):return ('sub',text)
def bullet(text):return ('bullet',text)
def fig(name,caption,width=510):return ('fig',name,caption,width)
def table(headers,rows,widths=None):return ('table',headers,rows,widths)
def eq(name,latex):return ('equation',name,latex)

page('Ứng dụng FP Growth trong phân tích giỏ hàng bán lẻ','G10  |  Ứng dụng 1  |  Nội dung cho slide 1',[
 p('Báo cáo sử dụng dữ liệu Online Retail để tìm những sản phẩm thường xuất hiện trong cùng hóa đơn, từ đó đề xuất thử nghiệm gợi ý mua kèm và phối hợp sản phẩm. Phạm vi phân tích là thị trường Anh trong giai đoạn 01/12/2010 đến 09/12/2011. Đây là minh họa khai phá dữ liệu lịch sử, không đại diện cho thị trường hiện nay. [1]'),
 sub('Câu hỏi kinh doanh'),
 p('Sản phẩm bán chạy cho biết từng mặt hàng phổ biến đến đâu. Người quản lý còn cần biết nhóm hàng nào được mua cùng nhau và mối liên hệ đó có mạnh hơn mức xuất hiện ngẫu nhiên theo tần suất riêng của từng mặt hàng hay không.'),
 bullet('Những tập sản phẩm nào xuất hiện cùng nhau trong ít nhất một tỷ lệ hóa đơn đã chọn?'),
 bullet('Khi hóa đơn có A, B xuất hiện với tỷ lệ bao nhiêu và cao hơn mức phổ biến chung của B đến mức nào?'),
 bullet('Những phát hiện nào đủ rõ để đề xuất thử một gợi ý mua kèm hoặc bộ sản phẩm?'),
 fig('05_so_do_ung_dung','Hình 1. Vai trò của FP-Growth trong ứng dụng. Sơ đồ do tác giả xây dựng; cơ sở thuật toán [2], sinh luật [4].'),
 sub('Kết quả chính'),
 p(f'Phân tích giữ lại <b>{num(N)} hóa đơn</b> và <b>{num(S["n_products"])} mã hàng</b>. Với minimum support 2%, độ dài tập mục tối đa 3, FP-Growth tìm được <b>{num(S["n_itemsets"])} tập mục</b>. Lọc tiếp confidence từ 60% và lift từ 1,5 thu được <b>{num(S["n_rules"])} luật có hướng</b>. Các con số là kết quả chạy lại trong nghiên cứu này, không phải số liệu được trích từ bài báo FP-Growth. [5]'),
 p('Luật giữa hai mẫu bộ tách trà có 700 hóa đơn mua cùng, confidence 75,11% và lift 14,06. Kết quả tạo cơ sở chọn một giả thuyết kinh doanh để thử nghiệm; chưa chứng minh doanh thu hay lợi nhuận tăng. [5]'),
])

page('Dữ liệu và đơn vị phân tích','Nội dung cho slide 2',[
 p('Online Retail do Daqing Chen công bố trên UCI gồm 541.909 dòng và 8 trường trong tệp gốc. Một dòng mô tả một mặt hàng của hóa đơn; nhiều dòng có thể thuộc cùng một hóa đơn. Doanh nghiệp bán lẻ trực tuyến đăng ký tại Anh, chủ yếu bán quà tặng; nguồn dữ liệu cũng cho biết nhiều khách hàng là người mua sỉ. [1]'),
 table(['Khái niệm','Cách xác định trong báo cáo'],[
  ['Một giao dịch','Một mã InvoiceNo sau lọc'],
  ['Một item','Một StockCode hàng hóa hợp lệ'],
  ['Sự hiện diện','Có hoặc không có mã hàng trong hóa đơn; không nhân trọng số theo Quantity'],
  ['Quy mô sau lọc',f'{num(N)} hóa đơn; {num(S["n_products"])} mã hàng; trung vị 15 mã hàng mỗi hóa đơn'],
 ],[112,398]),
 p('Giữ thị trường United Kingdom; loại hóa đơn hủy, dòng có Quantity hoặc UnitPrice không dương và mã ngoài quy ước hàng hóa đã chọn. Cùng một sản phẩm lặp trong hóa đơn chỉ tính hiện diện một lần. Không loại hóa đơn chỉ vì thiếu CustomerID, vì đơn vị phân tích là hóa đơn. Chi tiết định lượng nằm ở phụ lục nguồn và tái lập. [5]'),
 fig('01_san_pham_pho_bien',f'Hình 2. Tám sản phẩm có mặt trong nhiều hóa đơn nhất. Mẫu số là {num(N)} hóa đơn; trục ngang đo tỷ lệ hiện diện, không đo số lượng bán hoặc doanh thu. Nguồn: tính từ [1], kết quả [5].'),
 p('<b>Cách đọc:</b> mặt hàng phổ biến chưa chắc tạo ra luật mua kèm đáng chú ý. Cần xét quan hệ giữa các mặt hàng thay vì suy luận từ thứ hạng bán chạy.'),
])

page('Phương pháp và các chỉ số đánh giá','Cơ sở đọc kết quả và hỗ trợ slide 4',[
 p('FP-Growth nén thông tin giao dịch vào FP-tree và khai phá qua các cây có điều kiện, tránh sinh tập ứng viên theo từng mức như Apriori. Trong ứng dụng này, đầu ra trực tiếp là tập mục thường xuyên; luật kết hợp được tạo ở bước tiếp theo. [2, 3]'),
 p('Gọi N là số hóa đơn, n(X) là số hóa đơn chứa toàn bộ tập X. Với luật A → B, hai vế không giao nhau. Các chỉ số sử dụng trong báo cáo như sau. [4]'),
 eq('support',r'\mathrm{support}(X)=\frac{n(X)}{N}'),
 p('<b>Support</b> đo mức phổ biến của một tập mục trong toàn bộ hóa đơn. Với luật A → B, support của luật là tỷ lệ hóa đơn chứa toàn bộ sản phẩm ở cả hai vế.'),
 eq('confidence',r'\mathrm{confidence}(A\rightarrow B)=\frac{n(A\cup B)}{n(A)}'),
 p('<b>Confidence</b> là tỷ lệ hóa đơn có B trong số hóa đơn có A. Đổi chiều luật có thể làm confidence thay đổi.'),
 eq('lift',r'\mathrm{lift}(A\rightarrow B)=\frac{\mathrm{confidence}(A\rightarrow B)}{\mathrm{support}(B)}=\frac{N\,n(A\cup B)}{n(A)\,n(B)}'),
 p('<b>Lift</b> đối chiếu sự đồng xuất hiện với trường hợp độc lập: lớn hơn 1 là liên hệ dương trong mẫu; bằng 1 tương ứng mức độc lập; nhỏ hơn 1 là liên hệ âm. Lift không phải hệ số tăng doanh thu.'),
 table(['Thiết lập','Giá trị','Ý nghĩa'],[
 ['Minimum support','2%',f'Ít nhất {num(S["min_count_main"])} trong {num(N)} hóa đơn'],
 ['Độ dài tập mục tối đa','3','Chỉ khai phá tập gồm 1 đến 3 sản phẩm'],
 ['Minimum confidence','60%','Lọc luật sau khi đã khai phá tập mục'],
 ['Minimum lift','1,5','Loại luật có liên hệ yếu theo tiêu chí đang xét'],
 ],[155,75,280]),
 p('Các ngưỡng là lựa chọn phục vụ phân tích và khả năng diễn giải; không được khẳng định là tối ưu cho doanh nghiệp. Phần khảo sát ngưỡng giúp nhìn rõ ảnh hưởng của lựa chọn này. [5]'),
])

rule_rows=[]
short=[('Túi hồng chấm bi','Túi đỏ Retrospot'),('Bộ tách trà xanh','Bộ tách trà hoa hồng'),('Đồng hồ xanh','Đồng hồ đỏ')]
for i,(r,(a,b)) in enumerate(zip(R,short),1):
 rule_rows.append([f'R{i}',f'{a} → {b}\n{r["a"]} → {r["b"]}',num(r['n_ab']),pct(r['support']),pct(r['confidence']),dec(r['lift'])])
page('Các mẫu mua cùng tiêu biểu','Nội dung cho slide 5',[
 p(f'Tại cấu hình chính, {num(S["n_itemsets"])} tập mục gồm 303 tập đơn, 106 tập đôi và 5 tập ba. Sau lọc có {num(S["n_rules"])} luật có hướng, kể cả các luật có nhiều sản phẩm ở một vế. Ba luật dưới đây minh họa ba nhóm hàng; không phải danh sách ba luật có lift cao nhất. [5]'),
 table(['Luật','Sản phẩm và mã hàng','Mua cùng','Support','Confidence','Lift'],rule_rows,[40,200,65,65,80,60]),
 fig('02_confidence_va_muc_nen',f'Hình 5. Tỷ lệ mua B khi có A so với mức phổ biến chung của B. N = {num(N)}; ánh xạ R1 đến R3 theo bảng trên. Nguồn: [5].'),
 p(f'<b>R1:</b> {num(R[0]["n_ab"])} hóa đơn chứa hai mẫu túi. B xuất hiện trong {pct(R[0]["n_b"]/N)} tổng hóa đơn, nhưng trong {pct(R[0]["confidence"])} hóa đơn có A. Đây là cơ sở xem xét gợi ý phối hợp các mẫu túi.'),
 p(f'<b>R2:</b> {num(R[1]["n_ab"])} hóa đơn chứa cả bộ tách trà xanh và bộ tách trà hoa hồng. Lift {dec(R[1]["lift"])} cho thấy hai mẫu xuất hiện cùng nhau nhiều hơn rõ rệt so với mức kỳ vọng độc lập.'),
 p(f'<b>R3:</b> {num(R[2]["n_ab"])} hóa đơn mua cùng hai màu đồng hồ. Mẫu này gợi ý khả năng người mua chọn nhiều biến thể cùng dòng; cần kiểm tra tiếp vai trò của khách mua sỉ trước khi thiết kế ưu đãi.'),
])

r=DEEP
both=r['n_ab'];aonly=r['n_a']-both;bonly=r['n_b']-both;neither=N-r['n_a']-r['n_b']+both
expected=r['n_a']*r['n_b']/N
page('Giải thích một luật từ các số đếm gốc','Nội dung cho slide 6',[
 p('Xét R2 với A = GREEN REGENCY TEACUP AND SAUCER (22697), B = ROSES REGENCY TEACUP AND SAUCER (22699). Dưới đây là bảng đếm trực tiếp từ toàn bộ hóa đơn sau lọc; kết quả đã được đối chiếu với đầu ra FP-Growth. [5]'),
 table(['','Có B','Không có B','Tổng'],[
 ['Có A',num(both),num(aonly),num(r['n_a'])],
 ['Không có A',num(bonly),num(neither),num(N-r['n_a'])],
 ['Tổng',num(r['n_b']),num(N-r['n_b']),num(N)],
 ],[170,110,120,110]),
 eq('support_example',subst['support_example']),
 p(f'Có {num(both)} trong {num(N)} hóa đơn chứa cả hai mẫu tách trà. Support {pct(r["support"])} được tính trên toàn bộ hóa đơn, không chỉ trên hóa đơn mua tách trà.'),
 eq('confidence_example',subst['confidence_example']),
 p(f'Trong {num(r["n_a"])} hóa đơn có A, {num(both)} hóa đơn cũng có B. Đây là ý nghĩa cụ thể của confidence {pct(r["confidence"])}; chưa phải xác suất một khách hàng mới sẽ chấp nhận gợi ý.'),
 eq('lift_example',subst['lift_example']),
 p(f'B vốn có mặt trong {pct(r["n_b"]/N)} tổng hóa đơn. Nếu sự hiện diện của A và B độc lập với các tần suất biên đang quan sát, số hóa đơn mua cùng kỳ vọng là khoảng {dec(expected,1)}. Thực tế có 700, tương ứng lift {dec(r["lift"])}.'),
 p(f'<b>Đổi chiều:</b> confidence B → A = 700/956 = {pct(r["reverse_confidence"])}. Hai chiều có cùng support và lift, nhưng confidence khác nhau. Vì vậy hệ thống gợi ý cần xét rõ sản phẩm đang có trong giỏ và sản phẩm được đề xuất.'),
])

page('Ảnh hưởng của minimum support','Nội dung cho slide 4 về lựa chọn cấu hình',[
 p('Giữ nguyên dữ liệu, giới hạn độ dài tập mục là 3, confidence từ 60% và lift từ 1,5; chỉ thay minimum support. Khi ngưỡng giảm, số mẫu và số luật tăng mạnh. Các kết quả sau là số lượng khai phá được, không phải độ chính xác dự báo. [5]'),
 table(['Minsup','Số HĐ tối thiểu','Tập mục','Luật sau lọc'],[
 [pct(v['minsup'],1),num(v['min_count']),num(v['itemsets']),num(v['rules'])] for v in S['sensitivity']
 ],[80,145,145,140]),
 fig('03_do_nhay_minsup','Hình 4. Số tập mục và luật ở các ngưỡng 1%, 2%, 3%, 5%. Bảng phía trên còn cung cấp ngưỡng 0,5%. Nguồn: [5].'),
 p('<b>Vì sao dùng 2% trong phần trình bày?</b> Ngưỡng này yêu cầu ít nhất 359 hóa đơn mua cùng, đồng thời cho 36 luật để xem xét. Đây là lựa chọn cân bằng quy mô bằng chứng và khối lượng kết quả cần đọc trong ví dụ này; chưa có tối ưu hóa lợi nhuận để xác nhận một ngưỡng kinh doanh tốt nhất.'),
 p('<b>Vì sao 5% không còn luật?</b> Chỉ còn 38 tập đơn và không còn tập đôi đạt support 5%, nên không đủ tập mục nhiều sản phẩm để sinh luật. Điều đó không có nghĩa FP-Growth chạy sai.'),
 p('Ngưỡng cao có thể bỏ qua các sản phẩm ngách; ngưỡng thấp có thể tạo quá nhiều luật và nhiều quan hệ khó sử dụng. Doanh nghiệp nên xét thêm số hóa đơn thực tế, biên lợi nhuận, tồn kho và khả năng hành động.'),
])

temp=S['temporal'];T=temp['rules']
page('Đối chiếu trên giai đoạn đến sau','Phụ lục kiểm tra kết quả theo thời gian',[
 p(f'Để kiểm tra mức ổn định theo thời gian, một lần phân tích riêng chỉ khai phá luật trên {num(temp["n_train"])} hóa đơn trước 01/10/2011. Sau đó giữ cố định ba luật đơn có support cao nhất từ giai đoạn này, bỏ cặp đảo chiều, rồi đếm lại trên {num(temp["n_test"])} hóa đơn từ 01/10 đến 09/12/2011. Không dùng giai đoạn sau để xây cây hoặc chọn các luật trong lần đối chiếu này. [5]'),
 fig('04_doi_chieu_thoi_gian','Hình 6. Confidence trước và sau mốc 01/10/2011. T1 = 22386 → 85099B; T2 = 22697 → 22699; T3 = 21931 → 85099B. T3 khác R3 của bảng minh họa toàn kỳ. Nguồn: [5].'),
 table(['Luật','HĐ mua cùng ở kỳ sau','Support kỳ sau','Confidence kỳ sau','Lift kỳ sau'],[
 [f'T{i+1}',num(v['test_n_ab']),pct(v['test_support']),pct(v['test_confidence']),dec(v['test_lift'])] for i,v in enumerate(T)
 ],[45,140,105,120,100]),
 p(f'Với luật bộ tách trà T2, confidence từ {pct(T[1]["train_confidence"])} ở kỳ trước lên {pct(T[1]["test_confidence"])} ở kỳ sau. Kỳ sau có {num(T[1]["test_n_a"])} hóa đơn chứa A, trong đó {num(T[1]["test_n_ab"])} cũng có B. Cả ba luật được kiểm tra vẫn có confidence trên 60% và lift trên 1,5.'),
 p('<b>Ý nghĩa:</b> ba quan hệ được chọn còn xuất hiện ở giai đoạn đến sau trong cùng bộ dữ liệu. Đối chiếu này hỗ trợ nhận xét về độ ổn định quan sát được, chưa đo khả năng làm tăng tỷ lệ mua khi triển khai gợi ý.'),
 p('<b>Giới hạn:</b> kỳ sau chứa mùa cuối năm và chỉ đến ngày 09/12; không phải một quý đầy đủ. Dữ liệu đến từ cùng doanh nghiệp và thuộc năm 2010–2011, nên cần đánh giá lại khi thay thị trường hoặc thời điểm.'),
])

page('Từ phát hiện dữ liệu đến quyết định kinh doanh','Nội dung cho slide 7',[
 p('Các luật tạo ra danh sách quan hệ cần xem xét. Quyết định triển khai còn phụ thuộc giá bán, biên lợi nhuận, tồn kho, đặc điểm người mua và mức độ phù hợp của sản phẩm. Các phương án dưới đây là đề xuất thử nghiệm dựa trên phát hiện; chưa được đánh giá bằng thử nghiệm bán hàng.'),
 sub('Gợi ý một mẫu túi khác khi đã có túi trong giỏ'),
 p(f'R1 có {num(R[0]["n_ab"])} hóa đơn mua cùng và confidence {pct(R[0]["confidence"])}. Có thể thử hiển thị mẫu túi đỏ khi giỏ có mẫu hồng chấm bi, với điều kiện mẫu đỏ chưa có trong giỏ và còn hàng. Cần kiểm tra đây là nhu cầu phối mẫu hay đặc điểm đặt hàng số lượng lớn.'),
 sub('Giới thiệu bộ phối hợp các mẫu tách trà'),
 p(f'R2 có support {pct(R[1]["support"])} và lift {dec(R[1]["lift"])}. Có thể thử một trang bộ sưu tập gồm mẫu xanh và mẫu hoa hồng, kèm lựa chọn mua từng mẫu. Dữ liệu chưa đủ để xác định có cần giảm giá hay giảm bao nhiêu.'),
 sub('Trưng bày nhiều màu của cùng dòng đồng hồ'),
 p(f'R3 ghi nhận {num(R[2]["n_ab"])} hóa đơn mua cùng hai màu. Có thể thử liên kết các biến thể trên trang sản phẩm. Vì nhiều khách trong dữ liệu là người mua sỉ [1], không suy diễn rằng mọi người mua lẻ đều có nhu cầu sở hữu nhiều đồng hồ.'),
 sub('Đánh giá bằng thử nghiệm có nhóm đối chứng'),
 p('Trong một thử nghiệm A/B, phân bổ ngẫu nhiên khách hàng hoặc phiên truy cập đủ điều kiện vào nhóm có và không có gợi ý. Quy định trước sản phẩm, quy tắc gợi ý, thời gian và thước đo. Có thể theo dõi tỷ lệ thêm sản phẩm được gợi ý, tỷ lệ hoàn tất đơn và lợi nhuận đóng góp trên mỗi đơn, đồng thời theo dõi hủy hoặc trả hàng.'),
 p('Chưa có số liệu giá vốn và thử nghiệm can thiệp trong phân tích này, vì vậy không đưa ra con số tăng doanh thu hay lợi nhuận. Một luật có lift cao chỉ cho thấy quan hệ đồng xuất hiện mạnh theo mẫu số đã xác định.'),
 sub('Kết luận trình bày'),
 p(f'FP-Growth giúp chuyển {num(N)} hóa đơn thành những tập mua cùng có thể giải thích bằng số đếm. Kết hợp support, confidence và lift giúp chọn quan hệ đáng xem xét hơn việc chỉ nhìn mặt hàng phổ biến. Giá trị kinh doanh cần được kiểm chứng bằng một hành động cụ thể và phép đo phù hợp.'),
])

script=[
 ('1','40 giây','Bài toán kinh doanh','Hình 1; trang 1',
  'Cửa hàng biết sản phẩm nào bán chạy nhưng còn cần biết các sản phẩm nào thường nằm trong cùng hóa đơn. Phần này dùng FP-Growth để tìm các nhóm mua cùng và xem chúng có thể hỗ trợ gợi ý mua kèm như thế nào.'),
 ('2','50 giây','Dữ liệu và giao dịch','Hình 2; trang 2',
  'Một dòng dữ liệu là một mặt hàng của hóa đơn, còn giao dịch dùng cho thuật toán là toàn bộ hóa đơn. Sau khi giới hạn thị trường Anh và lọc dữ liệu, tập phân tích có 17.901 hóa đơn và 3.785 mã hàng. Số lần mua nhiều đơn vị không được nhân vào support.'),
 ('3','55 giây','EDA và đặc điểm giỏ hàng','Hình 3; trang 3',
  'Giỏ hàng có trung vị 15 mã sản phẩm nhưng trung bình 26,46 mã, cho thấy phân bố lệch về phía giỏ lớn. Có 607 hóa đơn trên 100 mã, phù hợp với việc nguồn dữ liệu có khách mua sỉ. Tháng 11 có nhiều hóa đơn nhất; tháng 12 chỉ đến ngày 9 nên không thể so như một tháng đầy đủ.'),
 ('4','60 giây','Khảo sát và chọn cấu hình','Hình 4 và bảng ngưỡng; trang 5',
  'Nhóm thử nhiều mức support trên cùng dữ liệu. Từ 1% lên 2%, số luật giảm từ 634 xuống 36, giúp tập trung vào các quan hệ có ít nhất 359 hóa đơn mua cùng. Cấu hình chính giới hạn tập mục dài tối đa 3, confidence từ 60% và lift từ 1,5. Đây là ngưỡng phục vụ phân tích, chưa phải tối ưu lợi nhuận.'),
 ('5','70 giây','Ba kết quả tiêu biểu','Bảng R1 đến R3 và Hình 5; trang 6',
  'Tại support 2% và giới hạn ba sản phẩm, ta thu được 414 tập mục và 36 luật đạt ngưỡng. Ba ví dụ thuộc nhóm túi, tách trà và đồng hồ. Biểu đồ đối chiếu tỷ lệ B trong hóa đơn có A với tỷ lệ B trên toàn bộ hóa đơn, giúp thấy rõ mức liên hệ của từng cặp.'),
 ('6','75 giây','Giải thích luật bộ tách trà','Bảng số đếm và công thức thay số; trang 7',
  'Có 932 hóa đơn mua mẫu xanh, 956 hóa đơn mua mẫu hoa hồng và 700 hóa đơn mua cả hai. Do đó support là 3,91%, confidence 75,11% và lift 14,06. Lift không có nghĩa doanh thu tăng 14 lần; nó so sánh số lần đồng xuất hiện với kỳ vọng độc lập.'),
 ('7','70 giây','Đề xuất kinh doanh và giới hạn','Trang 8',
  'Từ dữ liệu có thể đề xuất thử gợi ý các mẫu túi, phối bộ tách trà hoặc liên kết các màu đồng hồ. Cần thử nghiệm với nhóm đối chứng và theo dõi cả lợi nhuận, không chỉ lượt nhấp. Kết luận là FP-Growth cung cấp quan hệ có bằng chứng để thử nghiệm, chứ bản thân thuật toán chưa tạo ra lợi nhuận.'),
]
page('Khung chuyển thành bảy slide','Tổng thời lượng mục tiêu 7 phút',[
 p('Mỗi slide nên giữ một thông điệp và một hình hoặc bảng chính. Các lời nói dưới đây là ý dẫn; luyện diễn giải theo cách hiểu của người trình bày, chỉ vào các con số trên hình và dành thời gian giải thích kết quả.'),
 *[b for no,time,title,visual,speech in script for b in [sub(f'Slide {no}  {title}  {time}'),p(f'<b>Tư liệu:</b> {visual}. {speech}')]],
 p('Nếu cần rút xuống 6 phút, rút gọn phần dữ liệu, EDA và đọc bảng kết quả; vẫn giữ giải thích một luật bằng số đếm. Đối chiếu theo thời gian ở trang 9 là phần dự phòng. Demo do thành viên 5 và 6 phối hợp thực hiện, dùng dữ liệu và cấu hình thống nhất với phần phân tích này.'),
])

qa=[
 ('Ứng dụng này thực sự dùng FP-Growth ở đâu',
  'Thuật toán nhận các tập mã sản phẩm của từng hóa đơn và tìm tập mục đạt minimum support. Bảng luật và gợi ý mua kèm được xây từ đầu ra đó. Chạy thống kê cặp đơn thuần mà không thực hiện khai phá tập mục thì chưa minh họa đúng vai trò FP-Growth.'),
 ('Vì sao dùng FP-Growth thay vì Apriori',
  'FP-Growth khai phá trên cấu trúc FP-tree và các bài toán có điều kiện, tránh sinh ứng viên theo từng mức [2]. Báo cáo này không đo thời gian hai thuật toán, nên không khẳng định nhanh hơn bao nhiêu lần trên bộ dữ liệu đang xét.'),
 ('Có tìm được tất cả tập mục thường xuyên không',
  'Cấu hình đã giới hạn max_len = 3, nên 414 là toàn bộ tập mục đạt ngưỡng trong phạm vi độ dài 1 đến 3. Không khẳng định đã liệt kê các tập dài hơn. Giới hạn giúp tập trung vào những nhóm nhỏ dễ trình bày.'),
 ('Vì sao vẫn giữ hóa đơn chỉ có một sản phẩm',
  'Đó vẫn là giao dịch hợp lệ trong tổng thể đang phân tích. Loại chúng sẽ đổi mẫu số support và thay đổi ý nghĩa tỷ lệ; vì vậy vẫn giữ cả hóa đơn không chứa bất kỳ item nào đạt ngưỡng lọc tần suất.'),
 ('Confidence cao có đủ để chọn luật không',
  'Chưa đủ. Nếu B vốn xuất hiện rất thường xuyên thì confidence có thể cao dù A cung cấp ít thông tin bổ sung. Cần đọc cùng support, số hóa đơn thực tế và lift; sau đó xem tính phù hợp về kinh doanh.'),
 ('Lift 14 có nghĩa gợi ý sẽ làm khách mua nhiều gấp 14 lần không',
  'Không. Nó so sánh mức đồng xuất hiện quan sát với kỳ vọng độc lập từ tần suất biên. Dữ liệu hóa đơn có thể chịu ảnh hưởng của mua sỉ, bộ sưu tập, mùa vụ hoặc yếu tố chưa đo; cần thử nghiệm can thiệp để kết luận tác động.'),
 ('Vì sao không xóa các dòng thiếu CustomerID',
  'Câu hỏi hiện tại là đồng xuất hiện theo hóa đơn, và InvoiceNo đã xác định giỏ hàng. Xóa chỉ vì thiếu CustomerID sẽ làm mất những giao dịch vẫn sử dụng được. Nếu chuyển sang cá nhân hóa theo người mua thì phải thiết kế lại dữ liệu và phạm vi.'),
 ('Làm sao biết số liệu báo cáo có thể kiểm chứng',
  'Mã nguồn đọc tệp UCI, lưu bảng số đếm, tập mục, luật và khảo sát ngưỡng. Các luật minh họa được đếm lại trực tiếp từ giỏ hàng rồi so sánh với kết quả thư viện. Tệp thống kê ghi phiên bản thư viện và mã SHA-256 của dữ liệu gốc. [5]'),
]
page('Câu hỏi phản biện và cách trả lời','Phụ lục học và bảo vệ phần ứng dụng',[
 *[b for title,answer in qa for b in [sub(title),p(answer)]],
])

refs=[
 ('[1] Dữ liệu','Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository. DOI 10.24432/C5BW33. Giấy phép CC BY 4.0.', 'https://archive.ics.uci.edu/dataset/352/online+retail'),
 ('[2] Cơ sở thuật toán','Han, J., Pei, J., Yin, Y., & Mao, R. (2004). Mining Frequent Patterns without Candidate Generation: A Frequent-Pattern Tree Approach. Data Mining and Knowledge Discovery, 8, 53–87. Mục 2 về FP-tree; mục 3 về khai phá.', 'https://www.cs.sfu.ca/~jpei/publications/dami03_fpgrowth.pdf'),
 ('[3] Cài đặt FP-Growth','Raschka và cộng sự. mlxtend user guide: fpgrowth. Hướng dẫn hàm khai phá frequent itemsets.', 'https://rasbt.github.io/mlxtend/user_guide/frequent_patterns/fpgrowth/'),
 ('[4] Định nghĩa chỉ số','Raschka và cộng sự. mlxtend user guide: association_rules. Công thức support, confidence và lift.', 'https://rasbt.github.io/mlxtend/user_guide/frequent_patterns/association_rules/'),
 ('[5] Kết quả tự tính','FP-Growth chạy ngày 03/11/2026: analysis.py, results/stats.json và các bảng tập mục, luật, ngưỡng. EDA bổ sung ngày 05/11/2026: eda_business.py, results/eda_stats.json. Biểu đồ số liệu được tạo từ các tệp kết quả đi kèm.',None),
]
page('Nguồn tham khảo và thông tin tái lập','Phụ lục kiểm chứng',[
 *[b for title,detail,url in refs for b in ([sub(title),p(detail)]+([('url',url)] if url else []))],
 sub('Các bước lọc và số dòng còn lại'),
 table(['Bước','Số dòng'],[[v['step'],num(v['rows'])] for v in S['stages']],[405,105]),
 p(f'Quy ước mã hàng: 5 chữ số và tối đa 2 chữ cái. Phiên bản: Python {S["python"]}; pandas {S["pandas"]}; NumPy {S["numpy"]}; mlxtend {S["mlxtend"]}. Giữ toàn bộ hóa đơn khi lọc item theo tần suất; tên hiển thị lấy mô tả phổ biến nhất của mã. SHA-256 của dữ liệu nằm trong results/stats.json. Ngày truy cập và tính toán: 03/11/2026.'),
])

# Add EDA after the dataset introduction, then arrange the report in the order
# problem -> dataset -> EDA -> metrics -> configuration -> mining -> interpretation.
page('EDA về kích thước giỏ hàng và thời gian','Nội dung cho slide 3',[
 p(f'EDA được thực hiện trên đúng {num(N)} hóa đơn dùng để khai phá. Mục đích là xem giỏ hàng có lớn nhỏ khác nhau ra sao và dữ liệu phân bố theo thời gian như thế nào, trước khi đọc các mẫu mua cùng. [5]'),
 fig('06_eda_gio_hang_va_thoi_gian',f'Hình 3. Phân bố kích thước giỏ và số hóa đơn hợp lệ theo tháng. Cột cam tháng 12/2011 chỉ gồm dữ liệu đến 09/12. N = {num(N)}; kích thước giỏ tính theo số mã hàng khác nhau. Nguồn: [5].'),
 p(f'<b>Kích thước giỏ:</b> trung vị {dec(E["basket_size_median"],0)}, trung bình {dec(E["basket_size_mean"])} và phân vị 95 là {dec(E["basket_size_p95"],0)} mã hàng. Có {num(E["single_item_baskets"])} hóa đơn một sản phẩm ({pct(E["single_item_share"])}), vẫn được giữ để support dùng đúng mẫu số.'),
 p(f'<b>Giỏ lớn:</b> {num(E["over100_baskets"])} hóa đơn có hơn 100 mã hàng ({pct(E["over100_share"])}); lớn nhất là {num(E["basket_size_max"])} mã. Giữ các hóa đơn này trong phạm vi phân tích, đồng thời lưu ý quan hệ mua cùng có thể phản ánh hoạt động mua sỉ. Chưa tự động kết luận chúng là dữ liệu sai.'),
 p(f'<b>Thời gian:</b> tháng 11/2011 có nhiều hóa đơn nhất ({num(E["peak_month_invoices"])}). Tháng 12/2011 chưa đầy đủ, nên số hóa đơn thấp hơn không đủ để kết luận nhu cầu giảm. Phân tích toàn kỳ chưa kiểm soát yếu tố mùa vụ.'),
])
eda_page=PAGES.pop()
original=PAGES.copy()
PAGES=[original[0],original[1],eda_page,original[2],original[5],original[3],original[4],original[7],original[6],original[8],original[9],original[10]]
PAGES[1]['blocks'].insert(3,p(f'<b>Kiểm tra dữ liệu gốc:</b> InvoiceNo và StockCode không thiếu. CustomerID thiếu {num(E["raw_missing_by_column"]["CustomerID"])} dòng ({pct(E["raw_missing_by_column"]["CustomerID"]/E["raw_rows"])}); vẫn có thể dùng hóa đơn để khai phá. Description thiếu {num(E["raw_missing_by_column"]["Description"])} dòng; mã hàng được dùng làm khóa. [5]'))

# A copy-ready slide outline is separate from the longer explanatory report.
slide_points=[
 ['Tìm nhóm sản phẩm thường xuất hiện trong cùng hóa đơn.','Dùng kết quả để đề xuất thử gợi ý mua kèm.','Dữ liệu Online Retail giai đoạn 2010–2011.'],
 [f'Dữ liệu gốc: {num(S["source_rows"])} dòng và 8 trường.',f'Phạm vi sau lọc: {num(N)} hóa đơn, {num(S["n_products"])} mã hàng.','Một InvoiceNo là một giỏ hàng; mỗi StockCode chỉ tính hiện diện một lần.'],
 [f'Trung vị {dec(E["basket_size_median"],0)} mã hàng/giỏ, trung bình {dec(E["basket_size_mean"])}.',f'{num(E["over100_baskets"])} giỏ trên 100 mã ({pct(E["over100_share"])}): lưu ý ảnh hưởng mua sỉ.',f'Tháng 11/2011 cao nhất: {num(E["peak_month_invoices"])} hóa đơn; tháng 12 chỉ đến ngày 9.'],
 [f'Minsup 2% tương ứng ít nhất {num(S["min_count_main"])} hóa đơn.', 'Max_len = 3; confidence từ 60%; lift từ 1,5.', 'Khảo sát 1% cho 634 luật, 2% cho 36 luật; chọn 2% để tập trung diễn giải.'],
 ['414 tập mục: 303 tập đơn, 106 tập đôi, 5 tập ba.','36 luật có hướng đạt cấu hình đã chọn.','Ba ví dụ: túi hồng → túi đỏ; tách xanh → tách hoa hồng; đồng hồ xanh → đồng hồ đỏ.'],
 ['A = tách xanh: 932 hóa đơn; B = tách hoa hồng: 956 hóa đơn; cùng A và B: 700.', 'Support = 700/17.901 ≈ 3,91%; confidence = 700/932 ≈ 75,11%.','Lift ≈ 14,06: quan hệ đồng xuất hiện mạnh so với mức độc lập.'],
 ['Đề xuất thử gợi ý mua kèm hoặc giới thiệu bộ sưu tập.','Xem xét tồn kho, giá và biên lợi nhuận trước khi triển khai.','Kiểm chứng hiệu quả bằng thử nghiệm; dữ liệu mua cùng chưa chứng minh tăng doanh thu.'],
]
outline=['# Nội dung đưa vào slide ứng dụng 1','', 'Mạch trình bày: bài toán → dữ liệu → EDA → cấu hình → kết quả → diễn giải → kết luận. Tổng thời lượng khoảng 7 phút.','']
for entry,points in zip(script,slide_points):
 no,time,title,visual,speech=entry
 outline.extend([f'## Slide {no}  {title}',f'Thời lượng: {time}.','',*['- '+pt for pt in points],'',f'Hình hoặc bảng: {visual}.','',f'Lời trình bày gợi ý: {speech}',''])
outline.extend(['## Phối hợp với thành viên 5 và 6','', 'Người phụ trách ứng dụng 1 bàn giao dữ liệu, EDA, cấu hình, kết quả và cách diễn giải. Thành viên 5 và 6 phụ trách phối hợp demo và dựng slide từ các nội dung này. Giữ cấu hình và phạm vi dữ liệu thống nhất để số liệu khớp báo cáo.','', 'Nguồn và kết quả tái lập: xem trang 12 của báo cáo và README.md.'])
(ROOT/'Noi_dung_7_slide_Ung_dung_1.md').write_text('\n'.join(outline),encoding='utf-8')

# Editable Markdown source uses the same content and figures as the PDF.
def plain(s):
 s=s.replace('<b>','**').replace('</b>','**').replace('<br/>','\n')
 return html.unescape(s)
md=[]
for page_i,pa in enumerate(PAGES,1):
 md.extend([f'# {pa["title"]}',f'*{pa["tag"]}*',''])
 for bl in pa['blocks']:
  if bl[0]=='p':md.extend([plain(bl[1]),''])
  elif bl[0]=='sub':md.extend(['## '+bl[1],''])
  elif bl[0]=='bullet':md.extend(['- '+bl[1],''])
  elif bl[0]=='fig':md.extend([f'![{bl[2]}](../../outputs/Ungdung1/figures/{bl[1]}.png)',bl[2],''])
  elif bl[0]=='equation':md.extend(['$$',bl[2],'$$',''])
  elif bl[0]=='table':
   md.append('| '+' | '.join(bl[1])+' |')
   md.append('| '+' | '.join(['---']*len(bl[1]))+' |')
   for row in bl[2]:md.append('| '+' | '.join(str(v).replace('\n','<br>') for v in row)+' |')
   md.append('')
  elif bl[0]=='url':md.extend([f'[Mở nguồn]({bl[1]})',''])
 md.extend(['---',''])
(REPORT_DIR/'Bao_cao_ung_dung_1_FP_Growth.md').write_text('\n'.join(md),encoding='utf-8')

for name,file in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf'),('Arial-Italic','ariali.ttf')]:
 pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/file)))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial-Italic',boldItalic='Arial-Bold')
INK=colors.HexColor('#17283D');NAVY=colors.HexColor('#173B5E');GRAY=colors.HexColor('#64748B')
styles={
 'title':ParagraphStyle('Title',fontName='Arial-Bold',fontSize=21,leading=26,textColor=colors.black,spaceAfter=14),
 'tag':ParagraphStyle('Tag',fontName='Arial',fontSize=9,leading=12,textColor=GRAY,spaceAfter=10),
 'p':ParagraphStyle('Body',fontName='Arial',fontSize=10.8,leading=15.3,textColor=INK,spaceAfter=8),
 'sub':ParagraphStyle('Sub',fontName='Arial-Bold',fontSize=11.4,leading=15,textColor=colors.black,spaceBefore=5,spaceAfter=5,keepWithNext=True),
 'bullet':ParagraphStyle('Bullet',fontName='Arial',fontSize=10.8,leading=15.3,leftIndent=12,firstLineIndent=-9,textColor=INK,spaceAfter=5),
 'caption':ParagraphStyle('Caption',fontName='Arial-Italic',fontSize=8.2,leading=11.2,textColor=GRAY,spaceAfter=10),
 'cell':ParagraphStyle('Cell',fontName='Arial',fontSize=9.1,leading=12.3,textColor=INK),
 'head':ParagraphStyle('Head',fontName='Arial-Bold',fontSize=9.1,leading=12.3,textColor=colors.white),
 'url':ParagraphStyle('Url',fontName='Arial',fontSize=8.2,leading=11,textColor=NAVY,spaceAfter=8,wordWrap='CJK'),
}
PDF=REPORT_DIR/'Bao_cao_ung_dung_1_FP_Growth.pdf'
W,H=A4;avail=W-84
story=[]
for i,pa in enumerate(PAGES):
 if i:story.append(PageBreak())
 story.extend([Paragraph(pa['tag'],styles['tag']),Paragraph(pa['title'],styles['title'])])
 for bl in pa['blocks']:
  kind=bl[0]
  if kind in ['p','sub']:story.append(Paragraph(bl[1],styles[kind]))
  elif kind=='bullet':story.append(Paragraph('• '+bl[1],styles['bullet']))
  elif kind=='url':story.append(Paragraph(f'<link href="{html.escape(bl[1],quote=True)}">{html.escape(bl[1])}</link>',styles['url']))
  elif kind=='fig':
   path=FIG_DIR/f'{bl[1]}.png'
   iw,ih=PILImage.open(path).size
   width=min(bl[3],avail);height=width*ih/iw
   story.append(KeepTogether([Image(str(path),width=width,height=height),Spacer(1,5),Paragraph(bl[2],styles['caption'])]))
  elif kind=='equation':
   path=FIG_DIR/f'formula_{bl[1]}.png'
   iw,ih=PILImage.open(path).size
   height=45;width=height*iw/ih
   if width>avail*.95:
    width=avail*.95;height=width*ih/iw
   story.extend([Image(str(path),width=width,height=height),Spacer(1,5)])
  elif kind=='table':
   widths=bl[3] or [avail/len(bl[1])]*len(bl[1])
   widths=[v/sum(widths)*avail for v in widths]
   data=[[Paragraph(html.escape(str(t)),styles['head']) for t in bl[1]]]
   for row in bl[2]:
    cells=[]
    for t in row:
     text=str(t)
     numeric=bool(text) and all(c.isdigit() or c in '.,% ' for c in text)
     st=ParagraphStyle('NumericCell',parent=styles['cell'],alignment=TA_CENTER) if numeric else styles['cell']
     cells.append(Paragraph(html.escape(text).replace('\n','<br/>'),st))
    data.append(cells)
   tb=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
   commands=[('BACKGROUND',(0,0),(-1,0),NAVY),('GRID',(0,0),(-1,-1),.5,colors.HexColor('#D9D9D9')),
      ('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
      ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]
   for rr in range(1,len(data)):
    if rr%2==0:commands.append(('BACKGROUND',(0,rr),(-1,rr),colors.HexColor('#F3F6F8')))
   tb.setStyle(TableStyle(commands));story.extend([tb,Spacer(1,10)])

def decorate(c,doc):
 c.setFont('Arial',8)
 c.setFillColor(GRAY)
 c.drawString(42,25,'G10  |  FP-Growth trong kinh doanh  |  Cập nhật 05/11/2026')
 c.drawRightString(W-42,25,str(doc.page))
 c.setTitle('Ứng dụng FP Growth trong phân tích giỏ hàng bán lẻ')
 c.setAuthor('G10')

doc=SimpleDocTemplate(str(PDF),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=36,bottomMargin=43)
doc.build(story,onFirstPage=decorate,onLaterPages=decorate)
print('PDF',PDF)
print('Planned sections',len(PAGES))
