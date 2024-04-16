# Upstage AI Lab 첫번째 과제.

## 프로젝트 소개

특정 코인 정보 사이트에서 크롤링한 코인 정보를 웹API 로 제공.

## 팀원

```
sarakael715@gmail.com
 - 가상화폐 및 블록체인 뉴스 분석 페이지
 - 상세 분석 페이지

dksjj123@gmail.com
 - 텔레그램 봇

cchok0330@naver.com
 - 
 
kerneld@naver.com
 - 국내 5대 거래소에서의 거래량 Top20 페이지
```

## Web API 목록

### * http://localhost:8000/docs
### * http://localhost:8000/api/v1/coin/TopCoinsByExchangeVolume



## 필요한 패키지 설치

```
pip install beautifulsoup4
pip install selenium
pip install webdriver-manager
pip install fastapi
pip install uvicorn[standard]
pip install tensorflow
pip install pillow
pip install numpy
pip install python-multipart
pip install python-telegram-bot
pip install streamlit
pip install snowflake-connector-python
pip install wordcloud
pip install gensim
pip install pyldavis
pip install scipy==1.12
pip install pyglet
pip install gtts
pip install seaborn
pip install plotly
pip install umap
pip install streamlit-tensorboard
```

## 약간의 소스코드 수정

* KeyStore/KeyStore.py 에서 자신의 환경에 맞게 값 수정.


## Snowflake 에서의 준비 작업

* BITDUCK DB 생성

* FIRSTPROJECT Schema 생성

* TOPCOINSBYEXCHANGEVOLUME Table 생성

```
create or replace TABLE BITDUCK.FIRSTPROJECT.TOPCOINSBYEXCHANGEVOLUME (
	INPUTDATE TIMESTAMP_NTZ(9) NOT NULL,
	RANK NUMBER(38,0) NOT NULL,
	ICONURL VARCHAR(16777216),
	NAME VARCHAR(16777216),
	ABBRNAME VARCHAR(16777216),
	PRICE VARCHAR(16777216),
	ONEHOURDELTA VARCHAR(16777216),
	ONEDAYDELTA VARCHAR(16777216),
	SEVENDAYDELTA VARCHAR(16777216),
	MARKETCAPITALIZATION VARCHAR(16777216),
	EXCHANGEVOLUME VARCHAR(16777216),
	CHARTURL VARCHAR(16777216),
	primary key (INPUTDATE, RANK)
);
```

## 실행 방법


### Streamlit 웹페이지
streamlit run app.py

### 텔레그램 봇 서비스
python TelegramBotMain.py

### WebAPI, 웹 스크래핑
python FastApiMain.py

