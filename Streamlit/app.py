import streamlit as st
from TopCoinsByExchangeVolume import getTopCoinsByExchangeVolume_WebApi
from TopCoinsByExchangeVolume import getTopCoinsByExchangeVolume_DB

st.set_page_config(
    page_title="프로젝트팀 10조",
)

st.sidebar.page_link("app.py", label="메인")
st.sidebar.page_link("pages/SpecificInfo.py", label="상세 정보")
st.sidebar.page_link("pages/EtcInfo.py", label="기타 정보")

st.title('국내 5대 거래소에서의 거래량 Top20')

#df = getTopCoinsByExchangeVolume_WebApi()
df = getTopCoinsByExchangeVolume_DB()

if df is not None:
        st.dataframe(
        df,
        use_container_width = True,
        column_config = {
            "아이콘" : st.column_config.ImageColumn(
                "아이콘", help="Streamlit app preview screenshots"
            ),
            "최근 7일" : st.column_config.ImageColumn(
                "최근 7일", help="Streamlit app preview screenshots"
            ),
        },
        hide_index = True,
    )
else:
    st.subheader('조금뒤에 다시 시도해주세요.')
