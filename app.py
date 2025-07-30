from fastapi import FastAPI
from routes.ndvi_timeseries import ndvi_router

app = FastAPI()

app.include_router(ndvi_router)
