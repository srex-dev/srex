import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        timeout_keep_alive=1800,  # 30 minutes
        timeout_graceful_shutdown=1800  # 30 minutes
    ) 