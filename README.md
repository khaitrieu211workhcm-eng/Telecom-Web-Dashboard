**HỆ THỐNG PHÂN TÍCH VÀ TRỰC QUAN HÓA CHỈ SỐ HIỆU NĂNG MẠNG VIỄN THÔNG**

(Telecom Web Dashboard) 

**I. GIỚI THIỆU**

Trong việc vận hành mạng viễn thông, việc xử lý các tập dữ liệu log KPI vô tuyến có định dạng phức tạp, phân mảnh và dung lượng lớn thường tiêu tốn thời gian khi thực hiện thủ công. Đề tài này được xây dựng nhằm phát triển một công cụ tự động hóa hỗ trợ công tác quản lý và giám sát mạng với các chức năng chính bao gồm:
- Tự động hóa tiền xử lý dữ liệu: Tự động xử lý ngoại lệ, các giá trị khuyết thiếu và chuẩn hóa cấu trúc dữ liệu đầu vào từ nhiều định dạng khác nhau (.xlsx, .csv).
- Lưu trữ dữ liệu tối ưu: Tích hợp hệ quản trị cơ sở dữ liệu quan hệ gọn nhẹ SQLite nhằm lưu trữ và truy vấn lịch sử dữ liệu một cách nhanh và ổn định.
- Trực quan hóa chuyên sâu: Sử dụng thư viện Plotly để xây dựng biểu đồ chuỗi thời gian, theo dõi biến động lưu lượng giữa các trạm phát sóng theo thời gian thực.
- Cảnh báo và phân tích chất lượng: Tự động lọc và trích xuất danh sách các cell có tỷ lệ tín hiệu trên nhiễu thấp, kèm theo tính năng xuất báo cáo định dạng .csv để đội ngũ có phương án can thiệp kịp thời.
  
**II. CÔNG CỤ**
- Ngôn ngữ lập trình: Python 
- Xử lý và tính toán dữ liệu: Pandas, NumPy
- GUI và ứng dụng Web: Streamlit
- Trực quan hóa dữ liệu: Plotly
- Cơ sở dữ liệu: SQLite3
- Môi trường phát triển: VS Code Studio 2022, Github

**III. CẤU TRÚC**
- .gitignore          # Cấu hình bỏ qua các tệp hệ thống và cơ sở dữ liệu cục bộ
- readme.md           # Tài liệu hướng dẫn sử dụng và triển khai dự án
- requirements.txt    # Danh sách các thư viện Python phụ thuộc
- app.py              # Chương trình chính (Giao diện Streamlit Dashboard)
- utils.py            # Thư viện hàm hỗ trợ xử lý ETL, làm sạch dữ liệu và tương tác SQLite
- Input/              # Thư mục lưu trữ dữ liệu log mẫu phục vụ kiểm thử (Input - Table.xlsx,network_kpi_report.csv)
