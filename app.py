import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# Function to Load Data
def load_data(file):
    file_extension = file.name.split('.')[-1].lower()

    try:
        if file_extension == 'csv':
            df = pd.read_csv(file)
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(file)
        elif file_extension == 'json':
            df = pd.read_json(file)
        else:
            st.error("Unsupported file format. Please upload a CSV, Excel, or JSON file.")
            return None
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Date'], inplace=True)
        df['Date'] = df['Date'].dt.date
    else:
        st.error("Dataset must contain a 'Date' column.")
        return None

    return df

# Set Page Configuration
st.set_page_config(page_title="KPITrendX: Plug-and-Play Analytics Platform", layout="wide")

# Apply Custom CSS for Enhanced Styling
st.markdown("""
    <style>
        /* 🎨 Background Theme with Soft Gradient */
        body {
            background: linear-gradient(135deg, #1e1e2e, #252542, #1e1e2e);
            color: white;
            font-family: 'Poppins', sans-serif;
        }

        /* 🌟 Glassmorphism KPI Cards */
        .kpi-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(12px);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            font-weight: bold;
            color: #ffffff;
            box-shadow: 0px 4px 12px rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease-in-out;
            transform: scale(1);
        }
        .kpi-card:hover {
            transform: scale(1.05);
            box-shadow: 0px 6px 14px rgba(50, 0, 255, 0.3);
        }

        /* 🔹 Sidebar with Smooth Animation */
        .st-emotion-cache-1wivap2 {
            background: linear-gradient(135deg, #1b1b30, #29294f);
            color: white;
            padding: 20px;
            border-radius: 10px;
            transition: background 0.3s ease-in-out;
        }

        /* 🎭 Animated Buttons */
        .stButton>button {
            background: linear-gradient(135deg, #0055aa, #660033);
            color: white;
            font-weight: bold;
            border-radius: 12px;
            padding: 12px 24px;
            transition: all 0.3s ease-in-out;
            border: none;
            cursor: pointer;
        }
        .stButton>button:hover {
            background: linear-gradient(135deg, #0077cc, #990033);
            box-shadow: 0px 4px 15px rgba(0, 85, 170, 0.5);
            transform: scale(1.08);
        }

        /* 📊 Animated Charts */
        .stPlotlyChart {
            border-radius: 12px !important;
            padding: 15px;
            background: #1e1e2e;
            box-shadow: 0px 4px 12px rgba(50, 0, 255, 0.2);
            transition: transform 0.3s ease-in-out;
        }
        .stPlotlyChart:hover {
            transform: scale(1.02);
            box-shadow: 0px 4px 14px rgba(255, 255, 255, 0.3);
        }

        /* 📄 Data Table Styling */
        .stDataFrame {
            border-radius: 10px;
            padding: 10px;
            background: #1e1e2e;
            color: white;
            box-shadow: 0px 4px 10px rgba(50, 0, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        /* 🏆 Title & Headings with Blue to Maroon Gradient */
        h1, h2 {
            font-weight: bold;
            text-align: center;
            background: linear-gradient(to right, #0055aa, #990033);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 2px 2px 10px rgba(0, 85, 170, 0.3);
            animation: fadeIn 1s ease-in-out;
        }
        h3 {
            text-align: center;
            background: linear-gradient(to right, #004488, #880022);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: fadeIn 1s ease-in-out;
        }

        /* 🔄 Fade-In Animation */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* 📌 Loading Spinner Animation */
        .loading-spinner {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px;
        }
        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid rgba(50, 0, 255, 0.3);
            border-top: 4px solid #0055aa;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

    </style>
""", unsafe_allow_html=True)

# Sidebar for File Upload
st.sidebar.header("📂 Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload your file (CSV, Excel, JSON)", type=['csv', 'xlsx', 'xls', 'json'])

if uploaded_file is not None:
    df = load_data(uploaded_file)

    if df is not None:
        st.sidebar.header("🎯 Filter Options")

        available_kpis = [col for col in df.columns if col != "Date" and pd.api.types.is_numeric_dtype(df[col])]

        if not available_kpis:
            st.sidebar.error("⚠️ No numeric KPIs found in the dataset.")
        else:
            selected_kpis = st.sidebar.multiselect("📊 Select KPIs to visualize", available_kpis, default=[])

            min_date, max_date = df['Date'].min(), df['Date'].max()
            date_range = st.sidebar.date_input("📅 Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)
            start_date, end_date = date_range

            df_filtered = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
            df_filtered = df_filtered.groupby('Date').mean(numeric_only=True).reset_index()

            st.title("📊 KPITrendX: Plug-and-Play Analytics Platform")

            # Time Interval Selection
            st.subheader("📆 Select Time Interval")
            time_intervals = {"1W": 7, "1M": 30, "3M": 90, "6M": 180, "1Y": 365, "3Y": 1095}
            selected_interval = st.radio("", list(time_intervals.keys()), horizontal=True)
            
            # Filter Data Based on Selected Time Interval
            days_back = time_intervals[selected_interval]
            end_date = pd.to_datetime(end_date)
            start_date = end_date - pd.Timedelta(days=days_back)
            
            df_filtered = df[(df['Date'] >= start_date.date()) & (df['Date'] <= end_date.date())]
            df_filtered = df_filtered.groupby('Date').mean(numeric_only=True).reset_index()
            
            import pandas as pd

            # Ensure 'Date' column is in datetime format
            df_filtered['Date'] = pd.to_datetime(df_filtered['Date'])
            
            if selected_interval == "3M":
                # Show previous 12 weeks' average values
                df_filtered = df_filtered.set_index('Date').resample('W').mean().reset_index()  # Weekly data
                df_filtered = df_filtered.tail(12)  # Show the last 12 weeks
                
            elif selected_interval == "6M":
                # Show week-wise average for the last 6 months
                df_filtered = df_filtered.set_index('Date').resample('W').mean().reset_index()  # Weekly data
                df_filtered = df_filtered.tail(26)  # Show the last 26 weeks (6 months)
                
            elif selected_interval == "1Y":
                # Show month-wise average for the last year
                df_filtered = df_filtered.set_index('Date').resample('M').mean().reset_index()  # Monthly data
                df_filtered = df_filtered[df_filtered['Date'] >= pd.to_datetime("today") - pd.DateOffset(years=1)]
                
            elif selected_interval == "3Y":
                # Show month-wise average for the last 3 years
                df_filtered = df_filtered.set_index('Date').resample('M').mean().reset_index()  # Monthly data
                df_filtered = df_filtered[df_filtered['Date'] >= pd.to_datetime("today") - pd.DateOffset(years=3)]

            
            # KPI Cards (Dynamic)
            if selected_kpis:
                st.markdown("<h3>📈 KPI Metrics</h3>", unsafe_allow_html=True)

                col1, col2, col3, col4 = st.columns(4)
                for kpi in selected_kpis:
                    current_value = df_filtered[kpi].iloc[-1] if not df_filtered.empty else 0
                    max_value = df_filtered[kpi].max() if not df_filtered.empty else 0
                    min_value = df_filtered[kpi].min() if not df_filtered.empty else 0
                    avg_value = df_filtered[kpi].mean() if not df_filtered.empty else 0

                    with col1:
                        st.markdown(f"<div class='kpi-card'>📍 Current {kpi}<br><b>{current_value:,.2f}</b></div>", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"<div class='kpi-card'>📊 Max {kpi}<br><b>{max_value:,.2f}</b></div>", unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"<div class='kpi-card'>📉 Min {kpi}<br><b>{min_value:,.2f}</b></div>", unsafe_allow_html=True)
                    with col4:
                        st.markdown(f"<div class='kpi-card'>📈 Avg {kpi}<br><b>{avg_value:,.2f}</b></div>", unsafe_allow_html=True)

            # Tabs for Trend and Comparison
            tab1, tab2 = st.tabs(["📈 KPI Trend Over Time", "📊 KPI Comparison"])

            with tab1:
                st.subheader("📈 KPI Trend Over Time")
                df_melted = df_filtered.melt(id_vars=["Date"], value_vars=selected_kpis, var_name="KPI", value_name="Value")

                fig = px.line(df_melted, x="Date", y="Value", color="KPI", title="KPI Trend Over Time", template="plotly_dark")
                fig.update_layout(
                    hovermode="x unified",
                    margin=dict(l=20, r=20, t=30, b=20),
                    paper_bgcolor="#222",
                    plot_bgcolor="#222",
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig, use_container_width=True)

                # KPI Distribution
                st.subheader("📊 KPI Distribution")
                fig_dist = px.histogram(df_filtered, x=selected_kpis, title="KPI Distribution", template="plotly_dark", barmode="overlay")
                st.plotly_chart(fig_dist, use_container_width=True)

                # Filtered Data Table
                st.subheader("📄 Filtered Data")
                st.dataframe(df_filtered[['Date'] + selected_kpis])

                # Download Button
                csv = df_filtered.to_csv(index=False).encode('utf-8')
                st.download_button(label="⬇️ Download as CSV", data=csv, file_name="KPI_report.csv", mime="text/csv")

            with tab2:
                st.subheader("📊 Compare KPIs Across Different Time Ranges")

                # KPI Selection
                comparison_kpi = st.selectbox("Select KPI for Comparison", df.columns[1:])
                
                st.subheader("📅 Choose Time Range Selection Method")
                selection_method = st.radio("Select Method", ["Custom Date Range", "Financial Year Dropdown"])
                
                # Convert Date column to datetime if not already
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
                
                # Create Financial Year column
                df["Financial Year"] = df["Date"].apply(lambda x: f"FY{x.year}-{str(x.year + 1)[-2:]}" if x.month >= 4 else f"FY{x.year - 1}-{str(x.year)[-2:]}")
                
                # Get unique financial years for dropdown
                financial_years = sorted(df["Financial Year"].unique())
                
                # **Option 1: Select Custom Date Ranges**
                if selection_method == "Custom Date Range":
                    st.subheader("📅 Select Custom Time Ranges for KPI Comparison")
                    
                    # Initialize session state for dynamic time ranges
                    if "time_ranges" not in st.session_state:
                        st.session_state.time_ranges = [(df['Date'].min(), df['Date'].max())]  # Default single range
                    
                    # Add button to dynamically add time ranges
                    if st.button("➕ Add Time Range"):
                        st.session_state.time_ranges.append((df['Date'].min(), df['Date'].max()))
                    
                    # Display time range selectors with delete option
                    for i, (start, end) in enumerate(st.session_state.time_ranges):
                        st.markdown(f"🔹 Time Range {i + 1}")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            start_date = st.date_input(f"Start Date {i + 1}", value=start, min_value=df['Date'].min(), max_value=df['Date'].max(), key=f"start_{i}")
                        with col2:
                            end_date = st.date_input(f"End Date {i + 1}", value=end, min_value=start_date, max_value=df['Date'].max(), key=f"end_{i}")
                        with col3:
                            if st.button(f"❌ Remove Time Range {i + 1}", key=f"remove_{i}"):
                                st.session_state.time_ranges.pop(i)
                                st.experimental_rerun()
                        
                        # Update session state
                        st.session_state.time_ranges[i] = (start_date, end_date)
                
                    # Process selected time ranges
                    comparison_data = []
                    for i, (start_date, end_date) in enumerate(st.session_state.time_ranges):
                        if start_date and end_date:
                            # Convert start_date and end_date to datetime64[ns]
                            start_date = pd.to_datetime(start_date)
                            end_date = pd.to_datetime(end_date)
                    
                            temp_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)].copy()

                        temp_df.loc[:, "Month"] = temp_df["Date"].dt.strftime('%b')
                
                        grouped_df = temp_df.groupby(["Financial Year", "Month"])[comparison_kpi].mean().reset_index()
                        grouped_df["Time Range"] = f"Range {i + 1}: {start_date} to {end_date}"
                        comparison_data.append(grouped_df)
                
                # **Option 2: Select Financial Year from Dropdown**
                else:
                    st.subheader("📆 Select Financial Years for KPI Comparison")
                    
                    selected_fy = st.multiselect("Choose Financial Years", financial_years)
                    
                    # Process selected financial years
                    comparison_data = []
                    for i, fy in enumerate(selected_fy):
                        temp_df = df[df["Financial Year"] == fy].copy()
                        temp_df.loc[:, "Month"] = temp_df["Date"].dt.strftime('%b')
                
                        grouped_df = temp_df.groupby(["Financial Year", "Month"])[comparison_kpi].mean().reset_index()
                        grouped_df["Time Range"] = f"Selected: {fy}"
                        comparison_data.append(grouped_df)
                
                # Merge data for visualization
                if comparison_data:
                    final_df = pd.concat(comparison_data)
                
                    # Define month order for fiscal year sorting (April to March)
                    month_order = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
                
                    # Ensure 'Month' is categorical with the correct order
                    final_df["Month"] = pd.Categorical(final_df["Month"], categories=month_order, ordered=True)
                
                    # Sort the DataFrame by Financial Year and Month
                    final_df = final_df.sort_values(["Financial Year", "Month"])
                
                    # Plot comparison chart with sorted x-axis
                    fig_comp = px.line(final_df, 
                                       x="Month", 
                                       y=comparison_kpi, 
                                       color="Financial Year",
                                       title="KPI Comparison Across Financial Years",
                                       template="plotly_dark", 
                                       markers=True)

                    # Add hover lines
                    fig_comp.update_traces(mode='lines+markers', hovertemplate='Month: %{x}<br>KPI: %{y}<extra></extra>')
                    fig_comp.update_layout(hovermode="x unified")  # Adds the vertical hover line
            
                    st.plotly_chart(fig_comp, use_container_width=True)
            
                    # Show Data Table
                    st.subheader("📄 Comparison Data Table (FY as Columns, Months as Rows)")

                    # Pivot DataFrame: Months as Index, Financial Years as Columns
                    pivot_df = final_df.pivot(index="Month", columns="Financial Year", values=comparison_kpi)
                    
                    # Reset index to keep Month as a column
                    pivot_df = pivot_df.reset_index()
                    
                    # Display in Streamlit
                    st.dataframe(pivot_df)

            
                    # Download Button
                    csv_comp = final_df.to_csv(index=False).encode('utf-8')
                    st.download_button(label="⬇️ Download Comparison Data", data=csv_comp, file_name="KPI_Comparison.csv", mime="text/csv")
                    
else:
    logo_path = "media/Test.mp4"

    def get_video_base64(video_path):
        """Reads a video file and encodes it in base64 format."""
        with open(video_path, "rb") as video_file:
            base64_video = base64.b64encode(video_file.read()).decode("utf-8")
        return base64_video
    
    if os.path.exists(logo_path):
        video_base64 = get_video_base64(logo_path)
        video_html = f"""
            <video width="100%" autoplay loop muted>
                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        """
        st.markdown(video_html, unsafe_allow_html=True)
        st.write("📂 Please upload a file to proceed.")
    
    else:
        st.warning("⚠️ No logo found. Please upload a file to proceed.")

   # Text with fade-in effect
    st.markdown("""
    <style>
        .typewriter-container {
            position: relative;
            width: 100%;
            height: 100px; /* Adjust this height to control the space for the text */
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .typewriter {
            font-size: 48px;
            font-weight: bold;
            font-family: 'Arial', sans-serif;
            text-align: center;
            color: transparent;
            background-image: linear-gradient(to right, blue, maroon);
            -webkit-background-clip: text;
            background-clip: text;
            white-space: nowrap;
            overflow: hidden;
            width: 0;
            animation: typing 5s steps(10, end) forwards, blink 0.75s step-end infinite;
        }

        @keyframes typing {
            0% {
                width: 0;
            }
            100% {
                width: 100%;
            }
        }

        @keyframes blink {
            50% {
                border-color: transparent;
            }
        }
    </style>

    <div class="typewriter-container">
        <div class="typewriter">adani</div>
    </div>
""", unsafe_allow_html=True)



st.markdown("---")
st.markdown("#### 🛠️ Created by Team ENOC", unsafe_allow_html=True)
