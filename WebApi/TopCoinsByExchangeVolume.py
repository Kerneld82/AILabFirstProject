from Crawling.TopCoinsByExchangeVolume import lock
from Crawling.TopCoinsByExchangeVolume import crawlingResultList

def Register(coinRouter):
    @coinRouter.get('/')
    def getGreetingMsg():
        return { 'message' : 'Greeting~' }

    @coinRouter.get('/TopCoinsByExchangeVolume')
    def getTopCoinsByExchangeVolume():
        with lock:
            return crawlingResultList
