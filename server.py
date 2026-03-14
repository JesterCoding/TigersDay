from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# 1. Mount the game folder FIRST so the browser can access the .py files
app.mount("/game", StaticFiles(directory="game"), name="game")

# 2. Mount the frontend folder SECOND to serve your index.html
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")