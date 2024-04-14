import streamlit as st

st.set_page_config(
    page_title="상세정보~",
)

st.sidebar.page_link("app.py", label="메인")
st.sidebar.page_link("pages/SpecificInfo.py", label="상세 정보")
st.sidebar.page_link("pages/EtcInfo.py", label="기타 정보")

st.title('상세 정보 페이지~~')
