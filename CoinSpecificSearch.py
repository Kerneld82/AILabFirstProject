import streamlit as st
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Start the WebDriver
options = Options()
options.add_argument("--headless")  # Run the browser in headless mode
driver = webdriver.Chrome(options=options)

# Upbit API URL
UPBIT_URL = "https://api.upbit.com/v1/ticker"

# Bitget API URL
BITGET_URL = "https://api.bitget.com/api/v2/spot/market/tickers"

# Tokenpost search URL
TOKENPOST_URL = "https://www.tokenpost.kr/search?v={coin}"  # 코인 이름을 {coin}으로 대체

def get_coin_info(exchange, coin):
    if exchange == "Upbit":
        response = requests.get(UPBIT_URL, params={"markets": f"KRW-{coin}"})
    elif exchange == "Bitget":
        response = requests.get(BITGET_URL, params={"symbol": f"{coin}USDT"})
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0] if exchange == "Upbit" else data["data"][0]
    return None
def display_coin_info(coin_info):
    if coin_info:
        st.write(f"**코인 이름:** {coin_info['market'] if 'market' in coin_info else coin_info['symbol']}")
        st.write(f"**현재 가격:** {coin_info['trade_price'] if 'trade_price' in coin_info else coin_info['lastPr']}")
        # 추가적인 정보 표시 (가격, 거래량 등)
def crawl_tokenpost(coin_name):
    # Tokenpost에서 코인 검색
    url = TOKENPOST_URL.format(coin=coin_name)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # 주요 뉴스 가져오기
    main_news = soup.select_one("#main_list_wrap > div > div > div.list_left_item > div:nth-child(1) > div.list_item_content > div.list_item_text > div > a")
    main_news_link = main_news['href'] if main_news else None
    # 관련 뉴스 가져오기
    related_news = soup.select("#main_list_wrap > div > div > div.list_left_item > div:nth-child(n+2) > div.list_item_content > div.list_item_text > div > a")
    # 주요 뉴스의 제목과 내용 가져오기
    main_news_title = main_news.text.strip() if main_news else "No title found"
    main_news_content = related_news[0].text.strip() if related_news else "No content found"
    # 주요 뉴스의 링크
    main_news_link = main_news_link if main_news_link else "No link found"
    # 관련 뉴스의 제목, 내용 및 링크 가져오기
    related_news_list = []
    for news in related_news[1:4]:  # 4개의 관련 뉴스 가져오기
        related_news_title = news.text.strip()
        related_news_link = news['href']
        related_news_list.append((related_news_title, related_news_link))
    return main_news_title, main_news_content, main_news_link, related_news_list

def showCoinSpecificSearch():
    # 페이지 타이틀 설정
    st.title("코인 상세 검색")
    # 코인 이름 입력
    coin = st.text_input("코인 이름 입력 (예: BTC)")
    # 검색 버튼 클릭 시 실행
    if st.button("검색"):
        upbit_info = get_coin_info("Upbit", coin)
        bitget_info = get_coin_info("Bitget", coin)
        if upbit_info or bitget_info:
            if upbit_info:
                st.write("**Upbit**")
                display_coin_info(upbit_info)
            if bitget_info:
                st.write("**Bitget**")
                display_coin_info(bitget_info)
            st.subheader("Tokenpost 뉴스")
            # Tokenpost 뉴스 크롤링
            title, content, main_news_link, related_news_list = crawl_tokenpost(coin)
            # 주요 뉴스 출력
            st.write(f"**주요 뉴스 제목:** {title}")
            st.write(f"**주요 뉴스 내용:** {content}")
            st.write(f"**주요 뉴스 링크:** https://www.tokenpost.kr{main_news_link}")
            # 관련 뉴스 출력
            st.write("**관련 뉴스**")
            for i, (related_title, related_link) in enumerate(related_news_list):
                st.write(f"{i+1}. [{related_title}](https://www.tokenpost.kr{related_link})")
        else:
            st.write("코인 정보를 가져올 수 없습니다.")
        