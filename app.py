import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

# Function to load and clean data
def load_data(file):
    file_extension = file.name.split('.')[-1].lower()
    
    if file_extension == 'csv':
        df = pd.read_csv(file)
    elif file_extension == 'xlsx' or file_extension == 'xls':
        df = pd.read_excel(file)
    elif file_extension == 'json':
        df = pd.read_json(file)

    else:
        st.error("Unsupported file format. Please upload a CSV, Excel, or JSON file.")
        return None

    # Date processing with multiple formats
    date_formats = ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%b/%Y']
    date_parsed = False
    for fmt in date_formats:
        try:
            df['Date'] = pd.to_datetime(df['Date'], format=fmt, errors='coerce')
            if df['Date'].notna().all():
                date_parsed = True
                break
        except Exception as e:
            continue

    if not date_parsed:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Fallback

    df.dropna(subset=['Date'], inplace=True)
    df['Date'] = df['Date'].dt.date  # Keep only the date part

    return df

# Streamlit App Layout
st.set_page_config(page_title="📊 KPI Analytics Dashboard", layout="wide")

# Sidebar Layout
st.sidebar.header("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload your file (CSV, Excel, JSON)", type=['csv', 'xlsx', 'xls', 'json'])

# Main dashboard layout
if uploaded_file is not None:
    df = load_data(uploaded_file)

    if df is not None:
        st.sidebar.header("Filter Options")

        # Check if 'Date' column exists and is valid
        if 'Date' not in df.columns or df['Date'].isnull().all():
            st.sidebar.error("The dataset must contain a valid 'Date' column.")
        else:
            # KPI selection from metadata
            available_kpis = [col for col in df.columns if col != "Date"]
            selected_kpis = st.sidebar.multiselect("Select KPIs to visualize", available_kpis, default=available_kpis[:3])

            # Ensure valid date values
            min_date, max_date = df['Date'].min(), df['Date'].max()

            if pd.notna(min_date) and pd.notna(max_date):
                date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], 
                                                   min_value=min_date, max_value=max_date)
                start_date, end_date = date_range
                filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
            else:
                st.sidebar.error("Date column contains invalid values. Please check your data.")
                filtered_df = df

            # Display the KPI cards
            st.title("📊 KPITrendX: Plug-and-Play Analytics Platform")
            col1, col2, col3, col4 = st.columns(4)
            for kpi in selected_kpis:
                col1.metric(f"Current {kpi}", filtered_df[kpi].iloc[-1])
                col2.metric(f"Max {kpi}", filtered_df[kpi].max())
                col3.metric(f"Min {kpi}", filtered_df[kpi].min())
                col4.metric(f"Average {kpi}", round(filtered_df[kpi].mean(), 2))

            # Night/Day Mode Toggle
            dark_mode = st.sidebar.checkbox("Enable Dark Mode")
            if dark_mode:
                st.markdown('<style>body {background-color: #2e2e2e; color: white;} </style>', unsafe_allow_html=True)
            else:
                st.markdown('<style>body {background-color: white; color: black;} </style>', unsafe_allow_html=True)

            # Interactive Chart (Zoom, Color selection)
            st.subheader("KPI Visualization (Interactive)")
            for kpi in selected_kpis:
                fig = px.line(filtered_df, x="Date", y=kpi, title=f"{kpi} Trend Over Time", 
                              color_discrete_sequence=["blue"])
                fig.update_layout(
                    xaxis_rangeslider_visible=True,
                    xaxis=dict(showgrid=True),
                    yaxis=dict(showgrid=True),
                    template="plotly_dark" if dark_mode else "plotly"
                )
                st.plotly_chart(fig, use_container_width=True)

            # Display the filtered data in table
            st.subheader("Filtered Data")
            st.write(filtered_df[['Date'] + selected_kpis])

            # Data download options
            st.subheader("Download Report")
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download as CSV", data=csv, file_name="report.csv", mime="text/csv")

            excel_writer = pd.ExcelWriter("report.xlsx", engine='xlsxwriter')
            filtered_df.to_excel(excel_writer, index=False)
            excel_writer.close()
            with open("report.xlsx", "rb") as f:
                st.download_button(label="Download as Excel", data=f, file_name="report.xlsx", mime="application/vnd.ms-excel")

else:
    st.info("Please upload a file (CSV, Excel, or JSON) to proceed.")

# Footer
st.markdown("---")
st.markdown("#### Created by Developers")
