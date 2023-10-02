import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.routes import contacts, auth, users

limiter = Limiter(key_func=get_remote_address, application_limits=["20/60seconds"])

app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

origins = ["http://localhost:3000", "http://localhost:63342"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(users.router, prefix="/api")


@app.get("/")
async def root():
    """
The root function returns a JSON object with the message &quot;Tomato&quot;.

:return: A dictionary, which is converted to json by default
:doc-author: Trelent
"""
    return {"message": "Tomato"}


@app.get("/api/database_checker")
def healthchecker(db: Session = Depends(get_db)):
    """
    The healthchecker function is a simple function that checks if the database is configured correctly.
    It does this by executing a SQL query and checking if it returns any results. If it doesn't, then there's something wrong with the database configuration.

    :param db: Session: Pass the database session to the function
    :return: A dictionary with a message
    :doc-author: Trelent"""
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
