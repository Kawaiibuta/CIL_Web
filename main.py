from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import temp
from routers import model
from routers import data

app = FastAPI()
app.include_router(temp.router)
app.include_router(model.router)
app.include_router(data.router)
app.mount("/", StaticFiles(directory="static"), name="static")

