import requests
import pandas as pd
from bs4 import BeautifulSoup
from telegram import Bot
import asyncio
import requests
import json
import pyglet
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import snowflake.connector as sf
import pandas as pd
from gtts import gTTS
import os
from datetime import datetime, timedelta
from KeyStore import KeyStore

def snow_flake(title, contents, url, sentiment, dates) :
    
    # 아무것도 들어오지 않을때 예외처리
    try :
        # Snowflake 연결 설정
        conn = sf.connect(
            connection_name="myconnection",
        )
        cursor = conn.cursor()

        cursor.execute("USE DATABASE BITDUCK")
        cursor.execute("USE SCHEMA FIRSTPROJECT")
        # 스테이지 생성
        cursor.execute("CREATE OR REPLACE STAGE MY_STAGE")
        # 테이블 생성
        i= 11
        table_name = f"TEST{i}"
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            title VARCHAR(16777216),
            contents VARCHAR(16777216),
            date VARCHAR(16777216),
            url VARCHAR(16777216),
            sentiment VARCHAR(16777216)
        )
        """)
        # 콤마 제거
        title = title.replace(',', ' ')
        contents = contents.replace(',', ' ')
        sentiment = sentiment.replace(',', ' ')
        # 따옴표 제거
        title = title.replace("'", ' ')
        contents = contents.replace("'", ' ')
        sentiment = sentiment.replace("'", ' ')
        # 데이터 삽입 쿼리 실행
        cursor.execute(f"""
            MERGE INTO {table_name} AS target
            USING (SELECT '{url}' as url) AS source
            ON target.url = source.url
            WHEN NOT MATCHED THEN
                INSERT (title, contents, date, sentiment, url)
                VALUES ('{title}', '{contents}', '{dates}', '{sentiment}', '{url}')
        """)


        # 연결 종료
        conn.close()
    except TypeError:
        return None
async def play_alert_sound():
    try:
        # 알림 오디오 파일 재생
        alert_music = pyglet.media.load("alert.mp3")
        alert_music.play()
        
        # 알림 오디오 파일 재생 완료 대기
        await asyncio.sleep(alert_music.duration)
        
        # 메시지 오디오 파일 재생
        message_music = pyglet.media.load("message.mp3")
        message_music.play()
        
        # 메시지 오디오 파일 재생 완료 대기
        await asyncio.sleep(message_music.duration)
        
        
    except Exception as e:
        print("오디오 재생 오류 발생:", e)
async def tts_telegram_alert(message, sentiment):
    try:
        # Sentiment 분석 결과에 따른 음성 텍스트 생성
        if float(sentiment.split()[3][:-1]) > 33:
            tts_text = "negative"
        elif float(sentiment.split()[5][:-1]) > 33:
            tts_text = "positive"
        else:
            tts_text = "neutral"
        '''
        # TTS 생성
        tts = gTTS(text=tts_text, lang='en')  # 'en'는 한국어 설정입니다.
        '''
        # TTS 생성 (영어로 설정)
        tts_en = gTTS(text=tts_text, lang='en')  # 'en'는 영어 설정입니다.
        tts_en.save("alert.mp3")
        
        # TTS 생성 (한글로 설정)
        tts_ko = gTTS(text=message, lang='ko')  # 'ko'는 한국어 설정입니다.
        tts_ko.save("message.mp3")
        
        
        
        # 오디오 파일 재생
        await play_alert_sound()

        # 임시 오디오 파일 삭제
        os.remove("alert.mp3")
        os.remove("message.mp3")
    except Exception as e :
        print("TTS 오류 발생:", e)

def summarize_text(title, content):
    headers = {
        "X-NCP-APIGW-API-KEY-ID": KeyStore.NaverOpenAPI_ClientId,
        "X-NCP-APIGW-API-KEY": KeyStore.NaverOpenAPI_ClientSecret,
        "Content-Type": "application/json"
    }
    language = "ko"  # 문서의 언어 (ko, ja)
    model = "news"  # 요약에 사용될 모델 (general, news)
    tone = "2"  # 요약 결과의 톤을 변환 (0, 1, 2, 3)
    summaryCount = "3"  # 요약할 문서의 문장 수
    url = "https://naveropenapi.apigw.ntruss.com/text-summary/v1/summarize"
    
    data = {
        "document": {
            "title": title,
            "content": content
        },
        "option": {
            "language": language,
            "model": model,
            "tone": tone,
            "summaryCount": summaryCount
        }
    }
    
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        response.raise_for_status()  # 오류가 있으면 예외를 발생시킵니다.
        response_dict = response.json()
        summary = response_dict.get("summary", "요약 내용을 찾을 수 없습니다.")
        return summary
    except requests.exceptions.HTTPError as err:
        return f"Error: {err}"
    except Exception as e:
        return f"Unexpected error: {e}"


def analyze_sentiment(text):
    url = "https://naveropenapi.apigw.ntruss.com/sentiment-analysis/v1/analyze"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": KeyStore.NaverOpenAPI_ClientId,
        "X-NCP-APIGW-API-KEY": KeyStore.NaverOpenAPI_ClientSecret,
        "Content-Type": "application/json"
    }
    data = {"content": text}
    
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        response.raise_for_status()  # 오류가 있으면 예외를 발생시킵니다.
        response_dict = response.json()
        confidence = response_dict["document"]["confidence"]
        result = f"Sentiment : [부정] {confidence['negative']:.0f}% [긍정] {confidence['positive']:.0f}% [중립] {confidence['neutral']:.0f}%"
        return result
    except requests.exceptions.HTTPError as err:
        return f"Error: {err}"
    except Exception as e:
        return f"Unexpected error: {e}"
async def get_xangle_alerts():
    try :
        # 생글 사이트에서 알람 가져오기
        # 사이트 열리는 걸 방지하여 headless 설정
        options = Options()
        options.headless = True
        # 사이트가 열리는걸 방지. headless라 하더라도 셀레늄이 작업하기 위해
        # 브라우저가 켜진다고 한다.
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        # 크롬 웹 드라이버 실행
        driver = webdriver.Chrome(options=options)

        # 웹 페이지 열기
        driver.get(KeyStore.XangleAlertUrl)
        wait = WebDriverWait(driver, 10)
        # 링크 최상단의 href 속성 가져오기
        url = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'list-content-mobile.mb8'))).get_attribute('href')
        # url 갱신
        driver.get(url)
        title = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__nuxt"]/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/div/div[1]/div/div[1]/div/p[2]'))).text
        content = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'detail-intelligence'))).text
        date = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'date'))).text
        alert_link = url
        # 알람 텍스트 추출
        title_text = title.strip() if title else "No title found"
        content_text = content.strip() if content else "No content found"
        summary = summarize_text(title_text, content_text)
        sentiment = analyze_sentiment(summary)
        
        # 하나의 문자열로 합치기
        combined_alert = f"Title: {title_text}\n\nSummary: {summary}\n\n{sentiment}\n\nLink: {alert_link}\n\n Dates: {date}"
        snow_flake(title, summary, alert_link, sentiment, date)
        return combined_alert, sentiment, title_text
    except NoSuchElementException:
            print("Element not found")
            return None
    except TimeoutException:
        print("Timeout: The website is under maintenance.")
        return None
async def get_naver_alerts():
    # 네이버 뉴스 검색어 '가상화폐' 알람 가져오기
    try :
        url = "https://search.naver.com/search.naver?where=news&query=%EA%B0%80%EC%83%81%ED%99%94%ED%8F%90&sm=tab_opt&sort=1&photo=0&field=0&pd=0&ds=&de=&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Add%2Cp%3Aall&is_sug_officeid=0&office_category=0&service_area=0"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # 알람 요소, 선택 요소를 선택하는 CSS 선택자를 찾습니다. 일반적으로 오른쪽 클릭 후 "Copy" 메뉴에서 "Copy selector"를 선택하면 해당 요소의 CSS 선택자를 클립보드에 복사할 수 있습니다.
        title = soup.select_one('#sp_nws1 > div > div > div.news_contents > a.news_tit')
        content = soup.select_one('#sp_nws1 > div > div > div.news_contents > div > div > a')
        alert_link = soup.select_one('#sp_nws1 > div > div > div.news_contents > a.news_tit')
        # 알람 텍스트 추출
        title_text = title.text.strip() if title else "No title found"
        content_text = content.text.strip() if content else "No content found"
        summary = summarize_text(title_text, content_text)
        sentiment = analyze_sentiment(summary)
        if alert_link :
            alert_link = alert_link.get('href')
        # 하나의 문자열로 합치기
        time = soup.select_one('#sp_nws1 > div > div > div.news_info > div.info_group > span')
        current_time = datetime.now()
        min=time.text[0]
        adjusted_time = current_time - timedelta(minutes=int(min))
        date = adjusted_time.strftime('%Y-%m-%d %H:%M')
        combined_alert = f"Title: {title_text}\n\nSummary: {summary}\n\n{sentiment}\n\nLink: {alert_link}"
        snow_flake(title_text, summary, alert_link, sentiment, date)
        return combined_alert, sentiment, title_text
    except NoSuchElementException:
            print("Element not found")
            return None
    except TimeoutException:
        print("Timeout: The website is under maintenance.")
        return None
async def get_coinness_alerts():
    # 코인니스 사이트에서 알람 가져오기
    try :
        url = KeyStore.CoinnessUrl
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # 알람 요소, 선택 요소를 선택하는 CSS 선택자를 찾습니다. 일반적으로 오른쪽 클릭 후 "Copy" 메뉴에서 "Copy selector"를 선택하면 해당 요소의 CSS 선택자를 클립보드에 복사할 수 있습니다.
        title = soup.select_one('#main_list_wrap > div > div > div.list_left_item > div:nth-child(1) > div.list_item_content > div.list_item_text > div > a')
        content = soup.select_one('#main_list_wrap > div > div > div.list_left_item > div:nth-child(1) > div.list_item_content > div.list_item_text > a > p')
        alert_link = soup.select_one('#main_list_wrap > div > div > div.list_left_item > div:nth-child(1) > div.list_item_content > div.list_item_text > a')
        date = soup.select_one('#main_list_wrap > div > div > div.list_left_item > div:nth-child(1) > div.list_item_content > div.list_item_write > div.date_item > span').get_text(strip=True)

        # 알람 텍스트 추출
        title_text = title.text.strip() if title else "No title found"
        content_text = content.text.strip() if content else "No content found"
        summary = summarize_text(title_text, content_text)
        sentiment = analyze_sentiment(summary)
        if alert_link :
            alert_link = alert_link.get('href')
        full_link = KeyStore.TokenPostUrl+alert_link
        snow_flake(title_text, summary, full_link, sentiment, date)
        
        # 하나의 문자열로 합치기
        combined_alert = f"Title: {title_text}\n\nSummary: {summary}\n\n{sentiment}\n\nLink: {full_link} "
        return combined_alert, sentiment, title_text
    except NoSuchElementException:
            print("Element not found")
            return None
    except TimeoutException:
        print("Timeout: The website is under maintenance.")
        return None
async def send_telegram_alert(bot_token, chat_id, message):
    try:
        # 텔레그램 봇을 통해 메시지 보내기
        bot = Bot(token=bot_token)
        await bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        print("Telegram 메시지 전송 중 오류 발생:", e)
async def main():
    # 텔레그램 봇 설정
    bot_token = KeyStore.Telegram_bot_token  # 본인의 봇 토큰으로 변경
    chat_id = KeyStore.Telegram_chat_id  # 본인의 채팅 ID로 변경
    previous_alert = None
    nav_previous_alert = None
    xan_previous_alert = None
    
    while True:
        # 코인니스 사이트에서 새로운 알람 가져오기
        new_alert, new_sentiment, new_title = await get_coinness_alerts()
        nav_new_alert, nav_sentiment, nav_title = await get_naver_alerts()
        xan_new_alert, xan_sentiment, xan_title = await get_xangle_alerts()
        # 이전 알람과 비교하여 변경된 경우에만 메시지 전송
        if new_alert != previous_alert:
            await send_telegram_alert(bot_token, chat_id, new_alert)
            await tts_telegram_alert(new_title, new_sentiment)
            previous_alert = new_alert
        if nav_new_alert != nav_previous_alert :
            await send_telegram_alert(bot_token, chat_id, nav_new_alert)
            await tts_telegram_alert(nav_title, nav_sentiment)
            nav_previous_alert = nav_new_alert
            
        if xan_new_alert != xan_previous_alert :
            await send_telegram_alert(bot_token, chat_id, xan_new_alert)
            await tts_telegram_alert(xan_title, xan_sentiment)
            xan_previous_alert = xan_new_alert
        
        # 3초마다 사이트 확인
        await asyncio.sleep(3)
if __name__ == "__main__":
    asyncio.run(main())