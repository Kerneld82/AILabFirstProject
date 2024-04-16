import streamlit as st
from TopCoinsByExchangeVolume import showTopCoinsByExchangeVolume
from CoinSpecificSearch import showCoinSpecificSearch
from Analyse import showNewsAnalyse
from Analyse import showSpecificAnalyse

st.set_page_config(
    page_title="프로젝트팀 10조",
)

# 사이드 바
st.sidebar.title("메뉴")
page = st.sidebar.radio("페이지 선택", ["국내 5대 거래소에서의 거래량 Top20 및 코인 상세 검색", "가상화폐 및 블록체인 뉴스 분석", "상세 분석"])

#
st.sidebar.page_link("pages/streamlit_langchain.py", label="LangChain")

#
if page == "국내 5대 거래소에서의 거래량 Top20 및 코인 상세 검색":
    showTopCoinsByExchangeVolume()
    showCoinSpecificSearch()

elif page == "가상화폐 및 블록체인 뉴스 분석":
    showNewsAnalyse()

elif page == "상세 분석":
    showSpecificAnalyse()
