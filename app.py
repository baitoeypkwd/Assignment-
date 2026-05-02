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
