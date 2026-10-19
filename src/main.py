import uvicorn
from fastapi import FastAPI

from api.routes import auth
from config import settings
from utils import setup_logging

setup_logging()

app = FastAPI()
app.include_router(auth)


def main():
    uvicorn.run(app, host=settings.run.host, port=settings.run.port)


if __name__ == "__main__":
    main()
