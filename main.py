from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter

from src.database.db import get_db
from src.routes.contacts import router as router_contact
from src.routes.auth import router as router_auth
from src.conf.config import config

app = FastAPI()
app.include_router(router_auth, prefix='/api')
app.include_router(router_contact, prefix='/api')

origins = [
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are needed by your app,
    such as connecting to databases or initializing caches.

    :return: A fastapilimiter object
    :doc-author: Trelent
    """
    r = await redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=0,
            password=None,
        )
    await FastAPILimiter.init(r)


@app.get("/")
def read_root():
    """
    The read_root function returns a dictionary with the key &quot;Hello&quot; and value &quot;World&quot;.


    :return: A dictionary with a single key and value
    :doc-author: Trelent
    """
    return {"Hello": "World"}


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):

    """
    The healthchecker function is a simple function that checks the health of the database.
    It does this by making a request to the database and checking if it returns any results.
    If there are no results, then we know something is wrong with our connection to the database.

    :param db: Session: Get the database session from the dependency
    :return: A dict with a message
    :doc-author: Trelent
    """
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
