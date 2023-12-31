from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Security,
    BackgroundTasks,
    Request,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from src.conf.messages import ACCOUNT_EXISTS_EXCEPTION, EMAIL_NOT_CONFIRMED, INVALID_PASSWORD, INVALID_EMAIL
from src.db.database import get_db
from src.repository import users as depo_users
from src.schemas.users import UserCreate, Token, RequestEmail, UserResponse
from src.services.auth import auth_service
from src.services.mail import send_email

router = APIRouter(
    prefix="/auth",
    tags=[
        "auth",
    ],
)
security = HTTPBearer()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
        body: UserCreate,
        background_tasks: BackgroundTasks,
        request: Request,
        db: Session = Depends(get_db),
):
    """
    The signup function creates a new user in the database.

    :param body: UserCreate: Get the user data from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background queue
    :param request: Request: Get the base url of the application
    :param db: Session: Get a database session
    :param : Get the user's email from the database
    :return: A dictionary with the user object and a detail message
    :doc-author: Trelent"""
    exist_user = await depo_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=ACCOUNT_EXISTS_EXCEPTION
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await depo_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, request.base_url)
    return {
        "user": new_user,
        "detail": "User successfully created. Check your email for confirmation.",
    }


@router.post("/login", response_model=Token)
async def login(
        body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    The login function is used to authenticate a user.

    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: Session: Access the database
    :return: An access token and a refresh token
    :doc-author: Trelent"""
    user = await depo_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_EMAIL
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=EMAIL_NOT_CONFIRMED
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_PASSWORD
        )
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await depo_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh_token", response_model=Token)
async def refresh_token(
        credentials: HTTPAuthorizationCredentials = Security(security),
        db: Session = Depends(get_db),
):
    """
    The refresh_token function is used to refresh the access token.
        The function takes in a refresh token and returns a new access_token and
        refresh_token pair.

    :param credentials: HTTPAuthorizationCredentials: Get the token from the request header
    :param db: Session: Get the database session
    :param : Get the user's email from the token
    :return: A dict with the token type, access_token and refresh_token
    :doc-author: Trelent"""
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await depo_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await depo_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await depo_users.update_token(user, refresh_token, db)
    return {
        "token_type": "bearer",
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
        It takes in the token that was sent to the user's email and uses it to get their email address.
        Then, it checks if there is a user with that email in the database. If not, an error message will be returned.
        If there is a user with that email, then we check if they have already confirmed their account or not (if they have already confirmed their account).
        If they haven't yet confirmed their account, then we update our database so that this particular users' &quot;confirmed&quot; field becomes True.

    :param token: str: Get the token from the url
    :param db: Session: Get the database session
    :return: A message that the email is already confirmed or a message that the email has been confirmed
    :doc-author: Trelent"""
    email = await auth_service.get_email_from_token(token)
    user = await depo_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await depo_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
        body: RequestEmail,
        background_tasks: BackgroundTasks,
        request: Request,
        db: Session = Depends(get_db),
):
    """
    The request_email function is used to send a confirmation email to the user.
        The function takes in an email address and sends a confirmation link to that address.
        If the user already has confirmed their account, they will be notified of this.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the server
    :param db: Session: Get the database session
    :param : Get the user's email and username from the database
    :return: A message to the user
    :doc-author: Trelent"""
    user = await depo_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Check your email for confirmation."}
