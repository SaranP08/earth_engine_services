from fastapi import FastAPI
from routes.ndvi_timeseries import router

app = FastAPI()

app.include_router(router)
