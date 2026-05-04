<<<<<<< HEAD
import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
import plotly.express as px

st.title("🍽️ Buffet Analysis Dashboard")

# -----------------------
# โหลดไฟล์
# -----------------------
file_name = "2026 Data Test1 Final - Busy Buffet Dataset.xlsx"
df = pd.read_excel(file_name)
df.columns = df.columns.str.strip()

# -----------------------
# แปลงเวลา
# -----------------------
def convert_time(t):
    if pd.isna(t): return pd.NaT
    if isinstance(t, str):
        if len(t.split(':')) == 2:
            t += ":00"
        return pd.to_timedelta(t, errors='coerce')
    elif isinstance(t, dt.time):
        return pd.to_timedelta(str(t))
    return pd.NaT

for col in ['queue_start', 'queue_end', 'meal_start', 'meal_end']:
    df[col] = df[col].apply(convert_time)

# -----------------------
# Feature Engineering
# -----------------------
df['is_walk_away'] = (~df['queue_start'].isna()) & (df['meal_start'].isna())
df['wait_time_min'] = (df['queue_end'] - df['queue_start']).dt.total_seconds() / 60.0
df['meal_duration_min'] = (df['meal_end'] - df['meal_start']).dt.total_seconds() / 60.0

df.loc[(df['meal_duration_min'] < 0) | (df['meal_duration_min'] > 600), 'meal_duration_min'] = np.nan

# -----------------------
# Sidebar Filter
# -----------------------
st.sidebar.header("Filter")
guest = st.sidebar.selectbox("Guest Type", ["All"] + list(df['Guest_type'].dropna().unique()))

if guest != "All":
    df = df[df['Guest_type'] == guest]

# -----------------------
# แสดงข้อมูลเบื้องต้น
# -----------------------
st.subheader("📊 Data Preview")
st.dataframe(df.head())

# -----------------------
# Summary Wait Time
# -----------------------
st.subheader("⏳ Wait Time Analysis")

wait_summary = df.groupby('Guest_type').agg(
    total_queue=('wait_time_min', 'count'),
    avg_wait=('wait_time_min', 'mean'),
    walk_aways=('is_walk_away', 'sum')
).reset_index()

wait_summary['walk_away_percent'] = (wait_summary['walk_aways'] / wait_summary['total_queue']) * 100

st.dataframe(wait_summary.round(2))

# กราฟ
fig1 = px.bar(
    wait_summary,
    x='Guest_type',
    y='avg_wait',
    color='Guest_type',
    text='avg_wait',
    title='Average Wait Time (Minutes)'
)

fig1.update_traces(texttemplate='%{text:.1f}', textposition='outside')
fig1.update_layout(showlegend=False)

st.plotly_chart(fig1)

# -----------------------
# Meal Duration Summary
# -----------------------
st.subheader("🍽️ Meal Duration Analysis")

meal_summary = df.groupby('Guest_type')['meal_duration_min'].describe().reset_index()

meal_summary = meal_summary[['Guest_type', 'count', 'mean', 'min', '50%', '75%', 'max']]

st.dataframe(meal_summary.round(2))

# Boxplot
fig3 = px.box(
    df.dropna(subset=['meal_duration_min']),
    x='Guest_type',
    y='meal_duration_min',
    color='Guest_type',
    title='Meal Duration Distribution'
)

fig3.update_layout(showlegend=False)

st.plotly_chart(fig3)
=======
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("🍽️ Busy Buffet Dashboard")

# -----------------------
# โหลดไฟล์
# -----------------------

df = pd.read_excel("2026 Data Test1 Final - Busy Buffet Dataset.xlsx")
st.write(df.head())

    # -----------------------
    # สร้างตัวแปร
    # -----------------------
    df['waiting_time'] = (df['queue_end'] - df['queue_start']).dt.total_seconds()/60
    df.loc[df['queue_start'].isna(), 'waiting_time'] = 0
    df.loc[df['queue_start'].notna() & df['queue_end'].isna(), 'waiting_time'] = 0

    df['dining_time'] = (df['meal_end'] - df['meal_start']).dt.total_seconds()/60

    df['walk_away'] = df['queue_start'].notna() & df['meal_start'].isna()

    # -----------------------
    # Filter
    # -----------------------
    st.sidebar.header("Filter")

    guest = st.sidebar.selectbox("Guest Type", ["All","In house","Walk in"])

    if guest != "All":
        df = df[df['Guest_type'] == guest]

    # -----------------------
    # Metrics
    # -----------------------
    st.subheader("📊 Key Metrics")

    col1, col2, col3 = st.columns(3)

    col1.metric("Avg Waiting Time", round(df['waiting_time'].mean(),2))
    col2.metric("Avg Dining Time", round(df['dining_time'].mean(),2))
    col3.metric("Walk-away Rate", str(round(df['walk_away'].mean()*100,2)) + "%")

    # -----------------------
    # Task 1: Waiting Time
    # -----------------------
    st.subheader("⏳ Waiting Time Distribution")

    df_wait = df[df['queue_start'].notna() & df['queue_end'].notna()]

    fig, ax = plt.subplots()
    ax.hist(df_wait['waiting_time'].dropna())
    ax.set_xlabel("Minutes")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)

    # -----------------------
    # Task 1: Guest Comparison
    # -----------------------
    st.subheader("👥 Waiting Time by Guest Type")

    fig, ax = plt.subplots()
    df_wait.boxplot(column='waiting_time', by='Guest_type', ax=ax)
    plt.suptitle("")
    st.pyplot(fig)

    # -----------------------
    # Dining Time
    # -----------------------
    st.subheader("🍽️ Dining Time Distribution")

    fig, ax = plt.subplots()
    ax.hist(df['dining_time'].dropna())
    ax.set_xlabel("Minutes")
    st.pyplot(fig)

    # -----------------------
    # Walk-away
    # -----------------------
    st.subheader("🚶 Walk-away Count")

    walk_counts = df['walk_away'].value_counts()

    fig, ax = plt.subplots()
    walk_counts.plot(kind='bar', ax=ax)
    st.pyplot(fig)

    # -----------------------
    # Raw Data
    # -----------------------
    st.subheader("📄 Data Preview")
    st.dataframe(df)

else:
    st.info("Please upload your cleaned CSV file")
>>>>>>> 3e2d8c87d2714846ebde603ad6377d88fa00f603
