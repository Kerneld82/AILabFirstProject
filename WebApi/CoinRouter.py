from fastapi import APIRouter
import WebApi.TopCoinsByExchangeVolume
import Crawling.TopCoinsByExchangeVolume
from threading import Thread

#
coinRouter = APIRouter(prefix='/api/v1/coin', tags=['coin'])
WebApi.TopCoinsByExchangeVolume.Register(coinRouter)

# 중복 실행 방지용
isAlreadyStartAllThread = False

def startAllThread():
    global isAlreadyStartAllThread
    
    if isAlreadyStartAllThread == False:
        isAlreadyStartAllThread = True
        startCrawlingTopCoinsByExchangeVolumeThread()

def startCrawlingTopCoinsByExchangeVolumeThread():
    print("crawlingTopCoinsByExchangeVolume Thread start.")
    th1 = Thread(target=Crawling.TopCoinsByExchangeVolume.crawlingTopCoinsByExchangeVolume)
    th1.start()
