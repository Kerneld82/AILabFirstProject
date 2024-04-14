import streamlit as st
import pandas as pd
import requests
import snowflake.connector as sf

def getTopCoinsByExchangeVolume_WebApi():
    try:
        response = requests.get('http://localhost:8000/api/v1/coin/TopCoinsByExchangeVolume')

        if response.status_code == 200:
            jsonDataList = response.json()
            
            if len(jsonDataList) == 0:
                return None
            
            iconUrlList = []
            nameList = []
            priceList = []
            oneHourDeltaList = []
            oneDayDeltaList = []
            sevenDayDeltaList = []
            marketCapitalizationList = []
            exchangeVolumeList = []
            chartUrlList = []

            for jsonData in jsonDataList:
                iconUrlList.append(jsonData['iconUrl'])
                nameList.append( f'{jsonData['name']} {jsonData['abbrName']}')
                priceList.append(jsonData['price'])
                oneHourDeltaList.append(jsonData['oneHourDelta'])
                oneDayDeltaList.append(jsonData['oneDayDelta'])
                sevenDayDeltaList.append(jsonData['sevenDayDelta'])
                marketCapitalizationList.append(jsonData['marketCapitalization'])
                exchangeVolumeList.append(jsonData['exchangeVolume'])
                chartUrlList.append(jsonData['chartUrl'])

            # DataFrame 생성
            df = pd.DataFrame({
                '아이콘' : iconUrlList,
                '코인명' : nameList,
                '가격' : priceList,
                '1H' : oneHourDeltaList,
                '24H' : oneDayDeltaList,
                '7D' : sevenDayDeltaList,
                '시가 총액' : marketCapitalizationList,
                '거래량(24시간)' : exchangeVolumeList,
                '최근 7일' : chartUrlList,
            })
            
            return df
        
    except:
        return None

    return None

def getTopCoinsByExchangeVolume_DB():
    try:
        # TODO
        # https://docs.snowflake.com/ko/developer-guide/python-connector/python-connector-connect 를 참고해서
        # %USERPROFILE%\AppData\Local\snowflake\connections.toml 파일 생성할것.
        conn = sf.connect(
            connection_name="myconnection",
        )
        
        cursor = conn.cursor()
        cursor.execute("USE DATABASE COINS")
        cursor.execute("USE SCHEMA TOPCOINSBYEXCHANGEVOLUME")

        # 가장 최신 날짜시간 구하기
        query = """
        SELECT TOP 1 INPUTDATE
        FROM
            TOPCOINSBYEXCHANGEVOLUME
        ORDER BY INPUTDATE DESC, RANK
        """

        cursor.execute(query)
        one_row = cursor.fetchone()
        latestDt = one_row[0]
        print("Date = ", latestDt)

        query = f"""
        SELECT TOP 20 *
        FROM
            TOPCOINSBYEXCHANGEVOLUME
        WHERE INPUTDATE='{latestDt}'
        ORDER BY INPUTDATE DESC, RANK
        """

        data = cursor.execute(query)
        tupList = data.fetchall()
        conn.close()
        
        if len(tupList) == 0:
            return None
        
        iconUrlList = []
        nameList = []
        priceList = []
        oneHourDeltaList = []
        oneDayDeltaList = []
        sevenDayDeltaList = []
        marketCapitalizationList = []
        exchangeVolumeList = []
        chartUrlList = []
        
        for tup in tupList:
            iconUrlList.append(tup[2])
            nameList.append( f'{tup[3]} {tup[4]}')
            priceList.append(tup[5])
            oneHourDeltaList.append(tup[6])
            oneDayDeltaList.append(tup[7])
            sevenDayDeltaList.append(tup[8])
            marketCapitalizationList.append(tup[9])
            exchangeVolumeList.append(tup[10])
            chartUrlList.append(tup[11])

        # DataFrame 생성
        df = pd.DataFrame({
            '아이콘' : iconUrlList,
            '코인명' : nameList,
            '가격' : priceList,
            '1H' : oneHourDeltaList,
            '24H' : oneDayDeltaList,
            '7D' : sevenDayDeltaList,
            '시가 총액' : marketCapitalizationList,
            '거래량(24시간)' : exchangeVolumeList,
            '최근 7일' : chartUrlList,
        })
        
        return df

    except:
        return None
    
    return None
