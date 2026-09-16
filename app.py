import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_and_clean_file, save_to_sqlite, load_from_sqlite

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="Telecom Web Dashboard",
    layout="wide"
)

st.title("Telecom Web Dashboard -  HỆ THỐNG PHÂN TÍCH VÀ TRỰC QUAN HÓA CHỈ SỐ HIỆU NĂNG MẠNG VIỄN THÔNG")
st.markdown("Hệ thống tự động hóa làm sạch log thô, trực quan hóa biến động lưu lượng và lọc cell suy hao theo ngưỡng cấu hình động.")

# Sidebar: Upload dữ liệu và xác định ngưỡng cần
st.sidebar.header("UPLOAD DATA")
uploaded_file_1 = st.sidebar.file_uploader("Upload (.xlsx)", type=["xlsx", "xls"])
uploaded_file_2 = st.sidebar.file_uploader("Upload (.csv)", type=["csv"])

df_processed = None

if uploaded_file_1 is not None:
    df_processed = load_and_clean_file(uploaded_file_1)
    if df_processed is not None:
        save_to_sqlite(df_processed)
        st.sidebar.success("Đã xử lý & lưu vào SQLite thành công!")

elif uploaded_file_2 is not None:
    df_processed = load_and_clean_file(uploaded_file_2)
    if df_processed is not None:
        save_to_sqlite(df_processed)
        st.sidebar.success("Đã xử lý & lưu vào SQLite thành công!")
else:
    # Load lại từ SQLite nếu đã từng chạy trước đó
    df_processed = load_from_sqlite()

if df_processed.empty:
    st.info("Upload (Excel hoặc CSV) để bắt đầu.")
else:
    # Bộ lọc không gian & cảnh báo động
    st.sidebar.markdown("---")
    st.sidebar.header("Bộ lọc Không gian & Ngưỡng")

    node_list = df_processed['Node_ID'].unique().tolist()
    selected_nodes = st.sidebar.multiselect("Chọn Trạm phát (Node_ID)", options=node_list, default=node_list)

    # Bổ sung Slider linh hoạt thay thế giá trị cố định -3 dB
    sinr_threshold = st.sidebar.slider(
        "Chọn ngưỡng cảnh báo SINR (dB)",
        min_value=-15.0,
        max_value=5.0,
        value=-3.0,
        step=0.5,
        help="Kéo thanh trượt để thay đổi mức ngưỡng đánh giá chất lượng tín hiệu suy hao."
    )

    df_filtered = df_processed[df_processed['Node_ID'].isin(selected_nodes)]

    # Tổng quan chỉ số
    col1, col2, col3, col4 = st.columns(4)
    total_records = len(df_filtered)
    unique_cells = df_filtered[['Node_ID', 'Sector_ID']].drop_duplicates().shape[0]
    avg_traffic = df_filtered['TRAFFIC_DL_MBPS'].mean() if 'TRAFFIC_DL_MBPS' in df_filtered.columns else 0

    degraded_count = 0
    if 'SINR_AVG' in df_filtered.columns:
        degraded_count = len(df_filtered[df_filtered['SINR_AVG'] < sinr_threshold])

    col1.metric("Tổng số bản ghi KPI", f"{total_records:,}")
    col2.metric("Số lượng Sector/Cell", f"{unique_cells}")
    col3.metric("Lưu lượng DL Trung bình", f"{avg_traffic:.2f} Mbps")
    col4.metric(f"Cảnh báo suy hao (SINR < {sinr_threshold}dB)", f"{degraded_count}")

    st.markdown("---")

    # Biểu đồ lưu lượng
    st.subheader("Biểu đồ Biến động Lưu lượng theo thời gian")
    if 'TRAFFIC_DL_MBPS' in df_filtered.columns and 'Report_Time' in df_filtered.columns:
        fig_traffic = px.line(
            df_filtered,
            x='Report_Time',
            y='TRAFFIC_DL_MBPS',
            color='Node_ID',
            markers=True,
            title="Biến động Traffic Download giữa các Trạm (Node)"
        )
        fig_traffic.update_layout(template="plotly_white", height=450)
        st.plotly_chart(fig_traffic, use_container_width=True)
    else:
        st.warning("Không tìm thấy trường TRAFFIC_DL_MBPS để vẽ biểu đồ.")

    st.markdown("---")

    # Lọc cell suy hao theo ngưỡng 
    st.subheader(f"Danh sách Cell Đang Suy Hao Chất Lượng (SINR < {sinr_threshold} dB)")
    if 'SINR_AVG' in df_filtered.columns:
        df_degraded = df_filtered[df_filtered['SINR_AVG'] < sinr_threshold].sort_values(by='SINR_AVG')

        if not df_degraded.empty:
            st.error(f"Phát hiện {len(df_degraded)} cell vi phạm ngưỡng SINR < {sinr_threshold} dB!")
            st.dataframe(df_degraded, use_container_width=True)

            csv_data = df_degraded.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Report Cell Suy Hao (.csv)",
                data=csv_data,
                file_name=f"degraded_cells_sinr_{sinr_threshold}.csv",
                mime="text/csv",
            )
        else:
            st.success(f"Đạt chất lượng tốt (Không có cell nào vi phạm ngưỡng SINR < {sinr_threshold} dB).")
    else:
        st.info("Không tìm thấy trường dữ liệu SINR_AVG.")

    # Truy cập bảng dữ liệu
    with st.expander("Bảng cơ sở dữ liệu sau khi làm sạch & lưu SQLite"):
        st.dataframe(df_filtered, use_container_width=True)