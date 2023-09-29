import pickle
from datetime import datetime, timedelta
from typing import Optional

import redis
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.db.database import get_db
from src.repository import users as repository_users


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    redis = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    def verify_password(self, plain_password, hashed_password):
        """
    The verify_password function takes a plain-text password and hashed
    password as arguments. It then uses the pwd_context object to verify that the
    plain-text password matches the hashed one.

    :param self: Make the function a method of the user class
    :param plain_password: Pass in the password that is entered by the user
    :param hashed_password: Verify the password that is stored in the database
    :return: True or false depending on if the password is correct
    :doc-author: Trelent
    """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
    The get_password_hash function takes a password as input and returns the hash of that password.
    The hash is generated using the pwd_context object, which is an instance of Flask-Bcrypt's Bcrypt class.

    :param self: Represent the instance of the class
    :param password: str: Get the password from the user
    :return: A password hash
    :doc-author: Trelent
    """
        return self.pwd_context.hash(password)

    async def create_access_token(
            self, data: dict, expires_delta: Optional[float] = None
    ):
        """
    The create_access_token function creates a new access token.
        Args:
            data (dict): A dictionary containing the claims to be encoded in the JWT.
            expires_delta (Optional[float]): An optional timedelta of seconds for the token's expiration time.

    :param self: Represent the instance of the class
    :param data: dict: Pass the data that will be encoded in the jwt
    :param expires_delta: Optional[float]: Set the expiration time of the access token
    :return: A jwt token
    :doc-author: Trelent
    """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=1)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"}
        )
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_access_token

    async def create_refresh_token(
            self, data: dict, expires_delta: Optional[float] = None
    ):
        """
    The create_refresh_token function creates a refresh token for the user.
        Args:
            data (dict): A dictionary containing the user's id and username.
            expires_delta (Optional[float]): The time in seconds until the refresh token expires. Defaults to None, which sets it to 7 days from now.

    :param self: Make the function a method of the class
    :param data: dict: Pass the data to be encoded into the token
    :param expires_delta: Optional[float]: Set the expiration time of the token
    :return: A jwt that contains the user's id, username, and email
    :doc-author: Trelent
    """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"}
        )
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
    The decode_refresh_token function is used to decode the refresh token.
    It will raise an exception if the token is invalid or has expired.
    If it's valid, it returns the email address of the user.

    :param self: Represent the instance of a class
    :param refresh_token: str: Pass in the refresh token that we want to decode
    :return: The email of the user who owns the refresh token
    :doc-author: Trelent
    """
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    async def get_current_user(
            self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
    ):
        """
    The get_current_user function is a dependency that will be used in the
        protected endpoints. It takes a token as an argument and returns the user
        associated with that token. If no user is found, it raises an exception.

    :param self: Access the class attributes
    :param token: str: Pass the token from the authorization header to this function
    :param db: Session: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:

            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        user = self.redis.get(f"user:{email}")
        if user is None:
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.redis.set(f"user:{email}", pickle.dumps(user))
            self.redis.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)
        return user

    def create_email_token(self, data: dict):
        """
    The create_email_token function takes a dictionary of data and returns a JWT token.
    The token is encoded with the SECRET_KEY and ALGORITHM defined in the class.
    The iat (issued at) claim is set to datetime.utcnow() which represents when the token was created,
    and exp (expiration time) claim is set to one day from now.

    :param self: Access the instance of a class
    :param data: dict: Pass the data to be encoded into the token
    :return: A jwt token
    :doc-author: Trelent
    """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=1)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "email_token"}
        )
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
    The get_email_from_token function takes a token as an argument and returns the email address associated with that token.
    The function first decodes the JWT using PyJWT's decode method, which returns a dictionary of payload data.
    If the scope is &quot;email_token&quot;, then we know this is an email verification token, so we return its subject (the user's email).
    Otherwise, if it isn't an email verification token or if there was some other error decoding it (like expired), then we raise HTTPException.

    :param self: Represent the instance of the class
    :param token: str: Pass in the token that was sent to the user's email
    :return: The email address of the user who is trying to verify their email address
    :doc-author: Trelent
    """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "email_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification",
            )


auth_service = Auth()
