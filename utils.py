"""
Module: utils.py
Mô tả: Thư viện hỗ trợ thực hiện quy trình Extract - Transform - Load,
làm sạch dữ liệu log và tương tác với cơ sở dữ liệu SQLite.
"""
import sqlite3
import pandas as pd
import numpy as np

# Tên cơ sở dữ liệu SQLite lưu trữ cục bộ
DB_NAME = "telecom_logs.db"


def load_and_clean_file(uploaded_file):
    """
    Thực hiện quy trình trích xuất và biến đổi dữ liệu (Extract, Transform & Load):
    - Đọc file linh hoạt theo định dạng (.csv phân cách bằng dấu ';' hoặc .xlsx).
    - Làm sạch các giá trị ngoại lệ, khuyết thiếu ('MISSING', 'Unknown', 'None', '').
    - Chuyển đổi định dạng dữ liệu từ dạng dọc (Long-format) sang dạng bảng chuẩn (Wide-format).
    - Chuẩn hóa kiểu dữ liệu thời gian và các chỉ số KPI vô tuyến.
    Parameters:
        uploaded_file: Đối tượng tệp tải lên từ giao diện người dùng.
    Returns:
        pd.DataFrame hoặc None: Trả về DataFrame đã được làm sạch và chuẩn hóa, 
                               hoặc None nếu xảy ra lỗi/file không hợp lệ.
    """
    if uploaded_file is None:
        return None

    file_name = uploaded_file.name
    try:
        # Bước 1: Nhận diện định dạng tệp và đọc dữ liệu tương ứng
        if file_name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=';')
        elif file_name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(uploaded_file)
        else:
            return None

        # Bước 2: Chuẩn hóa và làm sạch các giá trị lỗi/khuyết thiếu thành NaN
        df.replace(['MISSING', 'Unknown', 'None', ''], np.nan, inplace=True)
        
        # Ép kiểu dữ liệu giá trị KPI sang kiểu số thực
        df['KPI_Value'] = pd.to_numeric(df['KPI_Value'], errors='coerce')

        # Bước 3: Loại bỏ các bản ghi thiếu thông tin định danh cốt lõi
        core_columns = ['Report_Time', 'Node_ID', 'Sector_ID', 'KPI_Type', 'KPI_Value']
        df.dropna(subset=core_columns, inplace=True)

        # Bước 4: Chuyển đổi cấu trúc Long-format sang Wide-format (bảng chuẩn theo thời gian và trạm)
        pivot_df = df.pivot_table(
            index=['Report_Time', 'Node_ID', 'Sector_ID'],
            columns='KPI_Type',
            values='KPI_Value',
            aggfunc='first'
        ).reset_index()

        # Bước 5: Ép kiểu dữ liệu cột thời gian sang định dạng Datetime chuẩn
        pivot_df['Report_Time'] = pd.to_datetime(pivot_df['Report_Time'])

        return pivot_df

    except Exception as e:
        # Ghi log lỗi chi tiết phục vụ công tác gỡ lỗi (Debugging)
        print(f"[Lỗi xử lý file]: {e}")
        return None


def save_to_sqlite(df, table_name="kpi_clean_logs"):
    """
    Thực hiện giai đoạn tải dữ liệu (Load trong quy trình ETL):
    Lưu trữ DataFrame dữ liệu đã làm sạch vào cơ sở dữ liệu quan hệ SQLite cục bộ.
    Parameters:
        df (pd.DataFrame): Bảng dữ liệu sạch cần lưu trữ.
        table_name (str): Tên bảng trong cơ sở dữ liệu (mặc định: 'kpi_clean_logs').
    """
    if df is None or df.empty:
        return
    
    # Thiết lập kết nối và ghi dữ liệu (thay thế bảng cũ nếu đã tồn tại)
    conn = sqlite3.connect(DB_NAME)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.close()


def load_from_sqlite(table_name="kpi_clean_logs"):
    """
    Truy vấn và khôi phục dữ liệu lịch sử từ cơ sở dữ liệu SQLite cục bộ.
    Parameters:
        table_name (str): Tên bảng cần truy vấn (mặc định: 'kpi_clean_logs').
    Returns:
        pd.DataFrame: DataFrame chứa dữ liệu đã truy vấn, hoặc DataFrame rỗng nếu xảy ra lỗi.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        conn.close()

        # Đảm bảo chuyển đổi lại kiểu dữ liệu thời gian sau khi đọc từ SQLite
        if 'Report_Time' in df.columns:
            df['Report_Time'] = pd.to_datetime(df['Report_Time'])
            
        return df
    except Exception:
        return pd.DataFrame()