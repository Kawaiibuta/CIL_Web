from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import temp
from routers import model
from routers import data
from routers import train
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

app = FastAPI()
app.include_router(temp.router)
app.include_router(model.router)
app.include_router(data.router)
app.include_router(train.router)
app.mount("/", StaticFiles(directory="static"), name="static")

