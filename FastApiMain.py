if __name__ == "__main__":
    import uvicorn
    uvicorn.run("FastApiMain:app", reload=True)
    
else:
    from fastapi import FastAPI
    from WebApi.CoinRouter import coinRouter
    from WebApi.CoinRouter import startAllThread
    
    app = FastAPI()
    app.include_router(coinRouter)
    startAllThread()