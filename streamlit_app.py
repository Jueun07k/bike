import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 📌 데이터 불러오기 함수
@st.cache_data
def load_data():
    dfs = []
    for i in range(1, 102):
        url = f"https://raw.githubusercontent.com/Jueun07k/bike/main/split_data_utf8/bike_data_part_{i}.csv"
        try:
            df = pd.read_csv(url, encoding='cp949', errors='ignore')
            dfs.append(df)
        except Exception as e:
            st.warning(f"⚠️ 파일 로드 실패: {url}\n오류: {e}")

    if not dfs:
        st.error("📛 CSV 파일을 하나도 불러오지 못했습니다.")
        return pd.DataFrame(), pd.DataFrame()

    bike_df = pd.concat(dfs, ignore_index=True)

    # 날짜 및 시간 처리
    bike_df['대여일시'] = pd.to_datetime(bike_df['대여일시'], errors='coerce')
    bike_df['날짜'] = bike_df['대여일시'].dt.date
    bike_df['시간대'] = bike_df['대여일시'].dt.hour

    # 날씨 데이터 로드
    weather_url = "https://raw.githubusercontent.com/Jueun07k/bike/main/OBS_ASOS_DD_20250610143611.csv"
    try:
        weather_df = pd.read_csv(weather_url, encoding='utf-8', errors='ignore')
        weather_df['날짜'] = pd.to_datetime(weather_df['날짜'], errors='coerce').dt.date
    except Exception as e:
        st.error(f"📛 날씨 데이터 로드 실패: {e}")
        weather_df = pd.DataFrame()

    return bike_df, weather_df
# 🔄 데이터 불러오기
bike_df, weather_df = load_data()

# 🎯 주제 설명
st.title("서울시 공공자전거(따릉이) 이용 패턴 분석")
st.markdown("""
- 시간대/지역별 이용량 분석  
- 대여/반납이 많은 지점 시각화  
- 날씨와의 상관관계 탐색  
- 탄소절감 효과 추정
""")

# 📊 시간대별 이용량 분석
st.header("1. 시간대별 따릉이 이용량")
time_counts = bike_df['시간대'].value_counts().sort_index()
st.bar_chart(time_counts)

# 🌦 날씨와의 상관관계 분석
st.header("2. 날씨와 따릉이 이용량 관계")
use_by_day = bike_df.groupby('날짜').size().reset_index(name='대여건수')
merged = pd.merge(use_by_day, weather_df, on='날짜', how='inner')

st.line_chart(merged[['대여건수', '평균기온(°C)', '강수량(mm)']])

# 🌱 탄소 절감 추정 (간단 예시)
st.header("3. 탄소 절감 효과 추정")
# 평균 자전거 1km당 CO2 절감량 약 21g 가정
CO2_PER_RIDE_G = 300  # rough estimate
total_rides = len(bike_df)
total_co2_saved_kg = total_rides * CO2_PER_RIDE_G / 1000

st.metric("총 탄소 절감량 (kg)", f"{total_co2_saved_kg:,.0f}")
