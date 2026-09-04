import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="서울 연평균 기온 변화",
    page_icon="🌡️",
    layout="wide",
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 열 이름에 혹시 공백이 포함되어 있어도 처리
    df.columns = df.columns.str.strip()

    # 날짜를 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

    # 평균기온을 숫자로 변환
    df["평균기온"] = pd.to_numeric(df["평균기온"], errors="coerce")

    # 유효한 데이터만 사용
    df = df.dropna(subset=["날짜", "평균기온"])

    return df


st.title("🌡️ 서울의 100년 기온 변화")
st.write("서울의 일별 기상 데이터를 바탕으로 연평균 기온의 변화를 살펴봅니다.")

try:
    df = load_data()

    # 연도별 평균기온 계산
    df["연도"] = df["날짜"].dt.year
    annual = (
        df.groupby("연도", as_index=False)["평균기온"]
        .mean()
        .rename(columns={"평균기온": "연평균기온"})
    )

    # 화면 표시용 인덱스
    chart_data = annual.set_index("연도")

    # 주요 정보
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("관측 시작 연도", f"{annual['연도'].min()}년")

    with col2:
        st.metric("관측 종료 연도", f"{annual['연도'].max()}년")

    with col3:
        change = annual.iloc[-1]["연평균기온"] - annual.iloc[0]["연평균기온"]
        st.metric("첫해 대비 마지막 해 변화", f"{change:+.1f}℃")

    st.subheader("서울 연평균 기온 변화")

    st.line_chart(
        chart_data,
        y="연평균기온",
        x_label="연도",
        y_label="연평균 기온 (℃)",
        height=500,
    )

    st.caption(
        "※ 연평균 기온은 해당 연도의 일별 평균기온을 평균하여 계산했습니다."
    )

    with st.expander("연도별 연평균 기온 데이터 보기"):
        display_data = annual.copy()
        display_data["연평균기온"] = display_data["연평균기온"].round(2)
        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True,
        )

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.exception(e)
