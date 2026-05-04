import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. Page Configuration
# ---------------------------------------------------------
st.set_page_config(page_title="Busy Buffet Analytics", layout="wide", page_icon="🍳")
st.title("🍳 Hotel Amber 85: Busy Buffet Analytics")
st.markdown("Dashboard สำหรับวิเคราะห์ปัญหาและหาทางออกให้แคมเปญบุฟเฟต์อาหารเช้า")

# ---------------------------------------------------------
# 2. Data Loading & Cleaning
# ---------------------------------------------------------
@st.cache_data
def load_data():
    file_path = '2026 Data Test1 Final - Busy Buffet Dataset.xlsx'
    xls = pd.ExcelFile(file_path)
    
    dfs = []
    for sheet in xls.sheet_names:
        temp_df = pd.read_excel(file_path, sheet_name=sheet)
        temp_df['Date'] = sheet # ใช้ชื่อชีตเป็นวันที่
        dfs.append(temp_df)
        
    df = pd.concat(dfs, ignore_index=True)
    df.columns = df.columns.str.strip()
    
    # ฟังก์ชันแปลงเวลา
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
        
    # Feature Engineering
    df['is_walk_away'] = (~df['queue_start'].isna()) & (df['meal_start'].isna())
    df['wait_time_min'] = (df['queue_end'] - df['queue_start']).dt.total_seconds() / 60.0
    df['meal_duration_min'] = (df['meal_end'] - df['meal_start']).dt.total_seconds() / 60.0
    
    # Clean Outliers
    df.loc[(df['meal_duration_min'] < 0) | (df['meal_duration_min'] > 600), 'meal_duration_min'] = np.nan
    
    return df

df = load_data()

# ---------------------------------------------------------
# 3. Task 1: Staff Comments Verification
# ---------------------------------------------------------
st.header("📌 Task 1: Staff Comments Verification")
st.markdown("พิสูจน์คำพูดของพนักงานจากข้อมูลจริง")

tab1, tab2, tab3 = st.tabs(["Comment 1: รอนานจนทิ้งคิว", "Comment 2: ยุ่งทุกวัน", "Comment 3: นั่งแช่ทั้งวัน"])

with tab1:
    st.subheader("Comment 1: ลูกค้าหงุดหงิดที่ต้องรอนาน และมีคนทิ้งคิว")
    st.markdown("**บทสรุป: จริง (True)** - ทั้ง In-house และ Walk-in ต้องรอนานเฉลี่ย 28-38 นาที และมีอัตราการทิ้งคิวสูงโดยเฉพาะ In-house")
    
    col1, col2 = st.columns(2)
    with col1:
        wait_df = df.groupby('Guest_type').agg(avg_wait=('wait_time_min', 'mean')).reset_index()
        fig1 = px.bar(wait_df, x='Guest_type', y='avg_wait', text='avg_wait', 
                      title="เวลารอเฉลี่ย (นาที)", color='Guest_type',
                      color_discrete_map={"In house": "#1f77b4", "Walk in": "#ff7f0e"})
        fig1.update_traces(texttemplate='<b>%{text:.1f} Mins</b>', textposition='outside')
        fig1.update_layout(showlegend=False, template="plotly_white")
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        walkaway_df = df.groupby('Guest_type').agg(
            total_queue=('wait_time_min', 'count'),
            walk_aways=('is_walk_away', 'sum')
        ).reset_index()
        walkaway_df['walk_away_rate'] = (walkaway_df['walk_aways'] / walkaway_df['total_queue']) * 100
        fig2 = px.bar(walkaway_df, x='Guest_type', y='walk_away_rate', text='walk_away_rate',
                      title="อัตราการทิ้งคิว (Walk-away Rate %)", color='Guest_type',
                      color_discrete_map={"In house": "#1f77b4", "Walk in": "#ff7f0e"})
        fig2.update_traces(texttemplate='<b>%{text:.1f}%</b>', textposition='outside')
        fig2.update_layout(showlegend=False, template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Comment 2: ยุ่งมากทุกวัน ธุรกิจนี้เป็นไปไม่ได้")
    st.markdown("**บทสรุป: ไม่จริงทั้งหมด (Partially False)** - ไม่ได้ยุ่งทุกวัน วันธรรมดาลูกค้าน้อยกว่าวันหยุดสุดสัปดาห์ถึง 40%")
    
    vol_df = df.groupby('Date').agg(pax=('pax', 'sum')).reset_index()
    fig3 = px.bar(vol_df, x='Date', y='pax', text='pax', title="ปริมาณลูกค้าทั้งหมดในแต่ละวัน (Pax)",
                  labels={"Date": "วันที่ (รหัสชีต)", "pax": "จำนวนลูกค้า"})
    fig3.update_traces(texttemplate='<b>%{text}</b>', textposition='outside', marker_color='#2ca02c')
    fig3.update_layout(template="plotly_white")
    st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.subheader("Comment 3: Walk-in นั่งแช่ทั้งวัน ทำให้ไม่มีโต๊ะ")
    st.markdown("**บทสรุป: ไม่จริง (False)** - แม้ Walk-in จะนั่งนานกว่า แต่ 75% ของ Walk-in ทานเสร็จภายใน 91 นาที (1 ชม. ครึ่ง) ไม่มีใครนั่งทั้งวัน")
    
    fig4 = px.box(df.dropna(subset=['meal_duration_min']), x='Guest_type', y='meal_duration_min', 
                  color='Guest_type', title="การกระจายตัวของเวลานั่งทาน (นาที)",
                  color_discrete_map={"In house": "#1f77b4", "Walk in": "#ff7f0e"})
    fig4.update_layout(showlegend=False, template="plotly_white")
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# 4. Task 2 & 3: Management Actions
# ---------------------------------------------------------
st.header("🛠️ Task 2 & 3: Management Actions Evaluation")

col_a, col_b = st.columns([1, 1])

with col_a:
    st.subheader("🚫 Task 2: ทำไมนโยบายของผู้บริหารจึงไม่เวิร์ค")
    st.error("**1. ลดเวลาทานจาก 5 ชั่วโมงให้สั้นลง (สมมติเหลือ 3 ชม.)**\n\nไม่ช่วยแก้ปัญหา เพราะลูกค้ากว่า 95% ทานเสร็จภายใน 2 ชั่วโมงอยู่แล้ว การห้ามคนนั่ง 5 ชั่วโมงจึงแทบไม่มีผลต่อ Table Turnover")
    st.error("**2. ขึ้นราคาทุกวันเป็น 259 บาท**\n\nจากกราฟปริมาณลูกค้า วันธรรมดามีคนน้อยอยู่แล้ว หากขึ้นราคาวันธรรมดาอาจทำให้ลูกค้า Walk-in หายไปหมด ธุรกิจจะยิ่งแย่ลง")
    st.error("**3. ให้สิทธิ In-house แซงคิว**\n\nลูกค้า Walk-in คือกลุ่มหลัก (58% ของลูกค้าทั้งหมด) การให้แซงคิวจะทำให้ Walk-in ที่ปัจจุบันรอเฉลี่ย 38 นาทีอยู่แล้ว ต้องรอนานขึ้นไปอีก และอัตราการทิ้งคิว (Walk-away) จะพุ่งสูงจนกระทบรายได้")

with col_b:
    st.subheader("💡 Task 3: ข้อเสนอแนะที่เวิร์ค (Recommendation)")
    st.success("**ทางออกที่แนะนำ: เปลี่ยนเป็น Dynamic Pricing หรือจำกัดเวลาที่ 90 นาที**")
    st.markdown("""
    **เหตุผลที่แนะนำ:**
    * **Dynamic Pricing (159 บ. วันธรรมดา / 259 บ. เสาร์อาทิตย์):** ช่วยดึงลูกค้าในวันที่คนน้อย และช่วยกรองคน/เพิ่มกำไรในวันที่คิวล้น
    * **จำกัดเวลา 90 นาที:** จากข้อมูลพบว่า ค่า P75 ของ Walk-in คือ 91 นาที แปลว่าถ้าเราจำกัดเวลาที่ 90 นาที ลูกค้าส่วนใหญ่ (75%) จะไม่รู้สึกว่าถูกเร่ง แต่เราจะสามารถจัดการกลุ่มคนที่นั่งแช่ (25% ที่เหลือ) ให้ออกตรงเวลา ทำให้หมุนโต๊ะได้เร็วขึ้นอย่างมากในช่วง Peak Hour
    """)
    
    # โชว์ข้อมูลสนับสนุน (คนเกิน 90 นาที)
    df_meals = df.dropna(subset=['meal_duration_min'])
    over_90 = len(df_meals[df_meals['meal_duration_min'] > 90])
    total = len(df_meals)
    
    st.info(f"📊 **Data Fact:** มีลูกค้าเพียง **{round((over_90/total)*100, 1)}%** เท่านั้นที่ใช้เวลานั่งทานเกิน 90 นาที")