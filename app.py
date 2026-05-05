import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Busy Buffet Visuals", layout="wide")
st.title("Buffet Data Visualizations")
st.markdown("สำหรับดู Data Visualizations เพื่อนำไปวิเคราะห์ต่อในรายงาน")

# 2. Data Loading & Cleaning
@st.cache_data
def load_data():
    file_path = '2026 Data Test1 Final - Busy Buffet Dataset.xlsx'
    xls = pd.ExcelFile(file_path)
    
    dfs = []
    for sheet in xls.sheet_names:
        temp_df = pd.read_excel(file_path, sheet_name=sheet)
        temp_df['Date'] = sheet
        dfs.append(temp_df)
        
    df = pd.concat(dfs, ignore_index=True)
    df.columns = df.columns.str.strip()
    
    def convert_time(t):
        if pd.isna(t): return pd.NaT
        if isinstance(t, str):
            if len(t.split(':')) == 2: t += ":00"
            return pd.to_timedelta(t, errors='coerce')
        elif isinstance(t, dt.time):
            return pd.to_timedelta(str(t))
        return pd.NaT

    for col in ['queue_start', 'queue_end', 'meal_start', 'meal_end']:
        df[col] = df[col].apply(convert_time)
        
    df['is_walk_away'] = (~df['queue_start'].isna()) & (df['meal_start'].isna())
    df['wait_time_min'] = (df['queue_end'] - df['queue_start']).dt.total_seconds() / 60.0
    df['meal_duration_min'] = (df['meal_end'] - df['meal_start']).dt.total_seconds() / 60.0
    
    # Clean Outliers
    df.loc[(df['meal_duration_min'] < 0) | (df['meal_duration_min'] > 600), 'meal_duration_min'] = np.nan
    
    return df

df = load_data()

st.divider()

# 3. Data Visualizations 
# แถวที่ 1
col1, col2 = st.columns(2)

with col1:
    wait_df = df.groupby('Guest_type').agg(avg_wait=('wait_time_min', 'mean')).reset_index()
    fig1 = px.bar(
        wait_df, x='Guest_type', y='avg_wait', text='avg_wait', 
        title="1. Average Wait Time (Minutes)", color='Guest_type',
        color_discrete_map={"In house": "#1f77b4", "Walk in": "#ff7f0e"}
    )
    fig1.update_traces(texttemplate='<b>%{text:.1f} Mins</b>', textposition='outside')
    fig1.update_layout(showlegend=False, template="plotly_white", yaxis_title="Minutes", xaxis_title="")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    walkaway_df = df.groupby('Guest_type').agg(
        total_queue=('wait_time_min', 'count'),
        walk_aways=('is_walk_away', 'sum')
    ).reset_index()
    walkaway_df['walk_away_rate'] = (walkaway_df['walk_aways'] / walkaway_df['total_queue']) * 100
    fig2 = px.bar(
        walkaway_df, x='Guest_type', y='walk_away_rate', text='walk_away_rate',
        title="2. Walk-away Rate (%)", color='Guest_type',
        color_discrete_map={"In house": "#1f77b4", "Walk in": "#ff7f0e"}
    )
    fig2.update_traces(texttemplate='<b>%{text:.1f}%</b>', textposition='outside')
    fig2.update_layout(showlegend=False, template="plotly_white", yaxis_title="Percentage (%)", xaxis_title="")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True) # เว้นบรรทัด

# แถวที่ 2
col3, col4 = st.columns(2)

with col3:
    vol_df = df.groupby('Date').agg(pax=('pax', 'sum')).reset_index()
    fig3 = px.bar(
        vol_df, x='Date', y='pax', text='pax', 
        title="3. Total Customers per Day (Pax)",
        labels={"Date": "Date (Sheet Name)"}
    )
    fig3.update_traces(texttemplate='<b>%{text}</b>', textposition='outside', marker_color='#2ca02c')
    fig3.update_layout(template="plotly_white", yaxis_title="Total Pax")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    fig4 = px.box(
        df.dropna(subset=['meal_duration_min']), x='Guest_type', y='meal_duration_min', 
        color='Guest_type', title="4. Meal Duration Distribution (Minutes)",
        color_discrete_map={"In house": "#1f77b4", "Walk in": "#ff7f0e"}
    )
    fig4.update_layout(showlegend=False, template="plotly_white", yaxis_title="Minutes", xaxis_title="")
    st.plotly_chart(fig4, use_container_width=True)

st.divider()
st.caption("Data processed and visualized for Data Analytics Test.")