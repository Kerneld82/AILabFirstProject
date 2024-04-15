import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import snowflake.connector as sf
import time
from KeyStore import KeyStore

lock = threading.Lock()
crawlingResultList = []

def insertToDb(infoList):
    if len(infoList) == 0:
        return
    
    try:
        # TODO
        # https://docs.snowflake.com/ko/developer-guide/python-connector/python-connector-connect 를 참고해서
        # %USERPROFILE%\AppData\Local\snowflake\connections.toml 파일 생성할것.
        conn = sf.connect(
            connection_name="myconnection",
        )
        
        cursor = conn.cursor()
        cursor.execute("USE DATABASE BITDUCK")
        cursor.execute("USE SCHEMA FIRSTPROJECT")

        inputDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        for i, info in enumerate(infoList):
            query = f"""
                INSERT INTO TOPCOINSBYEXCHANGEVOLUME (INPUTDATE, RANK, ICONURL, NAME, ABBRNAME, PRICE, 
                    ONEHOURDELTA, ONEDAYDELTA, SEVENDAYDELTA, MARKETCAPITALIZATION, EXCHANGEVOLUME, CHARTURL)
                VALUES('{inputDate}', {i}, '{info['iconUrl']}', '{info['name']}', '{info['abbrName']}', 
                    '{info['price']}', '{info['oneHourDelta']}', '{info['oneDayDelta']}', '{info['sevenDayDelta']}', 
                    '{info['marketCapitalization']}', '{info['exchangeVolume']}', '{info['chartUrl']}')
            """
            
            cursor.execute(query)
            
        conn.close()

    except:
        print("Insert error..")
    

# 국내 5대 거래소(업비트, 빗썸, 코인원, 코빗, 고팍스)의 가격 기준으로 거래량 상위 20개 코인 정보
def crawlingTopCoinsByExchangeVolume():
    options = Options()
    options.headless = True

    #ChromeDriverManager.install()
    browser = webdriver.Chrome(options = options)
    #browser.implicitly_wait(time_to_wait=5)

    while True:
        print("Start crawling..")
        
        url = KeyStore.TopCoinsByExchangeVolumeUrl
        browser.get(url)
        time.sleep(3)   # TODO 더 좋은 방법이 없을까..

        # "한국 기준시가" 버튼 클릭
        elements = browser.find_elements(By.CLASS_NAME, 'exchange-button')
        elements[1].click()
        time.sleep(3)   # TODO

        element = browser.find_element(By.CLASS_NAME, 'list-cont')
        element = element.find_element(By.CLASS_NAME, 'table-cont')
        elements = element.find_elements(By.CLASS_NAME, 'table-row')

        with lock:
            crawlingResultList.clear()

            for elem in elements:
                iconUrl = elem.find_element(By.CLASS_NAME, 'bc-asset-coin').get_attribute('src')
                name = elem.find_element(By.CLASS_NAME, 'mr4').text
                abbrName = elem.find_element(By.CLASS_NAME, 'symbol').text

                tdList = elem.find_elements(By.TAG_NAME, 'td')
                
                price = tdList[2].text
                oneHourDelta = tdList[3].text
                oneDayDelta = tdList[4].text
                sevenDayDelta = tdList[6].text
                marketCapitalization = tdList[7].text
                exchangeVolume = tdList[8].text
                chartUrl = tdList[9].find_element(By.TAG_NAME, 'img').get_attribute('src')
                #print(chartUrl)
                
                crawlingResultList.append({"iconUrl" : iconUrl,
                                "name" : name,
                                "abbrName" : abbrName,
                                "price" : price,
                                "oneHourDelta" : oneHourDelta,
                                "oneDayDelta" : oneDayDelta,
                                "sevenDayDelta" : sevenDayDelta,
                                "marketCapitalization" : marketCapitalization,
                                "exchangeVolume" : exchangeVolume,
                                "chartUrl" : chartUrl})
        
            insertToDb(crawlingResultList)
        
        print("End crawling..")
        print("sleep thread 5 seconds..")
        time.sleep(5)

if __name__ == "__main__":
    print("before... ", crawlingResultList)
    crawlingTopCoinsByExchangeVolume()
    print("after... ", crawlingResultList)
